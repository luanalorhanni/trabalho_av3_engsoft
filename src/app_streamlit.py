import streamlit as st
import sys
import time
from pathlib import Path
import pandas as pd
import plotly.express as px #importação de ploty
from datetime import date

##Configuração de paths
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

##Models
from model.pedido import Pedido
from model.item import Item
from model.database import Database

##Controllers
from controler.pedidoControler import PedidoControler
from controler.itemControler import ItemControler
from controler.databaseControler import DatabaseControler
from controler.relatorioController import RelatorioControler

##Report
from report.relatorio1 import PDF

##Configuração da página
st.set_page_config(
    page_title="Pizza Mais - Sistema de Gestão",
    page_icon="🍕",
    layout="wide"
)

##Inicialização do banco de dados
@st.cache_resource
def init_database():
    database = Database('TESTE.db')
    cursor = DatabaseControler.conect_database(database.name)
    DatabaseControler.create_table_itens(cursor)
    DatabaseControler.create_table_pedidos(cursor)
    DatabaseControler.create_table_itens_pedidos(cursor)
    return database

database = init_database()

##Sidebar para navegação
st.sidebar.title("🍕 Pizza Mais")
st.sidebar.markdown("*Criando Sonhos*")
st.sidebar.markdown("---")


#adaptações: de selectbox para radio
opcao = st.sidebar.radio(
    "Escolha uma opção:",
    ["🏠 Início", "📝 Cadastrar Pedido", "🔍 Pesquisar Pedidos", "📊 Relatório", "🍽️ Inserir Itens Menu"]
)


##Página principal
if opcao == "🏠 Início":
    st.title("🍕 Pizza Mais - Sistema de Gestão")
    st.markdown("Seus sonhos tem formato e borda 😋")
    st.markdown("Estabelecimento: UFMA")
    st.markdown("---")
    
    #Dashboard com métricas
    col1, col2, col3 = st.columns(3)
    
    with col1: #coluna 1
        try:
            pedidos = PedidoControler.search_in_pedidos_all(database.name)
            total_pedidos = len(pedidos) if pedidos else 0
            st.metric("Total de Pedidos", total_pedidos)
        except:
            st.metric("Total de Pedidos", 0)
    
    with col2: #coluna 2
        try:
            faturamento = sum(pedido.valor_total for pedido in pedidos) if pedidos else 0
            st.metric("Faturamento Total", f"R$ {faturamento:.2f}")
        except:
            st.metric("Faturamento Total", "R$ 0,00")
    
    with col3: #coluna 3 
        try:
            itens_menu = ItemControler.mostrar_itens_menu(database.name)
            total_itens = len(itens_menu) if itens_menu else 0
            st.metric("Itens no Menu", total_itens)
        except:
            st.metric("Itens no Menu", 0)

    st.markdown("## 📊 Análises Visuais")
    
    #Dashboard com métricas
    col1, col2, col3 = st.columns(3)
    
     # Recuperar os pedidos e montar um DataFrame
    pedidos = PedidoControler.search_in_pedidos_all(database.name)
            
    if pedidos:
        df = pd.DataFrame([vars(p) for p in pedidos])
    
        with col1: #coluna 1
            try:         
            # Gráfico de Pizza por Status
                fig_status = px.pie(df, names='status', title='Distribuição por Status de Pedido')
                st.plotly_chart(fig_status, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar gráficos: {e}")
                    
        with col2: #coluna 2
            try:        
                # Gráfico de Pizza por Delivery (Sim/Não)
                fig_delivery = px.pie(df, names='delivery', title='Distribuição por Delivery')
                st.plotly_chart(fig_delivery, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar gráficos: {e}")

        with col3: #coluna 3
            try:
                #correção de coluna date do dataframe
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df['mês'] = df['date'].dt.to_period('M').astype(str)
                df_mensal = df.groupby('mês').size().reset_index(name='Quantidade')

                fig_mensal = px.bar(df_mensal, x='mês', y='Quantidade', title='Pedidos por Mês', text='Quantidade')
                st.plotly_chart(fig_mensal, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao gerar gráficos: {e}")

    else:
        st.warning("Não há dados de pedidos para exibir gráficos.")
    

# Opção de Cadastrar Pedido

elif opcao == "📝 Cadastrar Pedido":
    st.title("📝 Cadastrar Novo Pedido")
    st.markdown("---")

    from datetime import date
    import pandas as pd

    # Inicializa estados temporários
    if 'itens_pedido_temp' not in st.session_state:
        st.session_state.itens_pedido_temp = []
    if 'total_pedido_temp' not in st.session_state:
        st.session_state.total_pedido_temp = 0.0
    if 'pedido_finalizado' not in st.session_state:
        st.session_state.pedido_finalizado = False
    if 'resumo_pedido' not in st.session_state:
        st.session_state.resumo_pedido = {}

    # Se um pedido foi finalizado, mostra o resumo e opções
    if st.session_state.pedido_finalizado:
        st.success("✅ **Pedido Cadastrado com Sucesso!**")
        
        # Caixa com resumo do pedido
        with st.container():
            st.markdown(f"""
            📋 **Resumo do Pedido:**
            
            - **Número do Pedido:** #{st.session_state.resumo_pedido['numero']}
            - **Status:** {st.session_state.resumo_pedido['status'].title()}
            - **Data:** {st.session_state.resumo_pedido['data']}
            - **Delivery:** {st.session_state.resumo_pedido['delivery']}
            - **Endereço:** {st.session_state.resumo_pedido['endereco']}
            - **Valor Total:** R$ {st.session_state.resumo_pedido['valor']:.2f}
            - **Itens:** {st.session_state.resumo_pedido['qtd_itens']} tipo(s) de item(ns)
            """)
        
        st.info(f"O pedido #{st.session_state.resumo_pedido['numero']}, com status '{st.session_state.resumo_pedido['status']}', da data {st.session_state.resumo_pedido['data']}, foi adicionado!")
        
        # Botões para próxima ação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Cadastrar Novo Pedido", use_container_width=True):
                # Limpar todos os estados e começar novo pedido
                st.session_state.itens_pedido_temp = []
                st.session_state.total_pedido_temp = 0.0
                st.session_state.pedido_finalizado = False
                st.session_state.resumo_pedido = {}
                st.rerun()
        
        with col2:
            if st.button("🏠 Voltar ao Menu Principal", use_container_width=True):
                # Limpar estados e voltar ao menu
                st.session_state.itens_pedido_temp = []
                st.session_state.total_pedido_temp = 0.0
                st.session_state.pedido_finalizado = False
                st.session_state.resumo_pedido = {}
                st.session_state.opcao_selecionada = None
                st.rerun()
        
    else:
        # Código para cadastrar novo pedido (só executa se não estiver no resumo)
        
        ##--- Seção para Adicionar Itens ao Pedido ---
        st.subheader("Adicionar Itens ao Pedido")
    
        itens_disponiveis = ItemControler.mostrar_itens_menu(database.name)

        if not itens_disponiveis:
            st.warning("Não há itens cadastrados no menu. Por favor, cadastre itens primeiro na opção 'Inserir Itens Menu'.")
        else:
            opcoes_itens_dict = {f"{item.nome} (R$ {item.preco:.2f})": item for item in itens_disponiveis}
            opcoes_nomes = list(opcoes_itens_dict.keys())

            with st.form("form_adicionar_item_ao_pedido", clear_on_submit=True):
                col_item, col_qtd = st.columns([3, 1])
                with col_item:
                    item_selecionado_nome_display = st.selectbox(
                        "Selecione o item:",
                        opcoes_nomes,
                        key="select_item_form"
                    )
                with col_qtd:
                    quantidade = st.number_input(
                        "Quantidade:",
                        min_value=1,
                        value=1,
                        step=1,
                        key="quantidade_item_form"
                    )
                
                col_btn_add, col_btn_clear = st.columns(2)
                with col_btn_add:
                    adicionar_item_button = st.form_submit_button("Adicionar ao Pedido")
                with col_btn_clear:
                    limpar_itens_button_form = st.form_submit_button("Limpar Itens (Atual)")

                if adicionar_item_button:
                    if item_selecionado_nome_display:
                        item_obj = opcoes_itens_dict[item_selecionado_nome_display]
                        item_para_adicionar = {
                            "id": item_obj.id,
                            "nome": item_obj.nome,
                            "preco_unitario": item_obj.preco,
                            "quantidade": quantidade,
                            "subtotal": item_obj.preco * quantidade
                        }
                        st.session_state.itens_pedido_temp.append(item_para_adicionar)
                        st.session_state.total_pedido_temp += item_para_adicionar["subtotal"]
                        st.success(f"Adicionado {quantidade}x '{item_obj.nome}' (R$ {item_para_adicionar['subtotal']:.2f}) ao pedido.")
                    else:
                        st.error("Por favor, selecione um item para adicionar.")
                
                if limpar_itens_button_form:
                    st.session_state.itens_pedido_temp = []
                    st.session_state.total_pedido_temp = 0.0
                    st.info("Lista de itens do pedido temporário limpa.")
                    st.rerun()

        ##--- Exibir Itens Adicionados e Total ---
        if st.session_state.itens_pedido_temp:
            st.subheader("Itens no Pedido Atual")
            df_itens_pedido = pd.DataFrame(st.session_state.itens_pedido_temp)
            df_exibir = df_itens_pedido[['nome', 'quantidade', 'preco_unitario', 'subtotal']].copy()
            df_exibir.columns = ['Sabor', 'Qtd', 'Preço Unitário (R$)', 'Subtotal (R$)']
            df_exibir['Preço Unitário (R$)'] = df_exibir['Preço Unitário (R$)'].apply(lambda x: f"R$ {x:.2f}")
            df_exibir['Subtotal (R$)'] = df_exibir['Subtotal (R$)'].apply(lambda x: f"R$ {x:.2f}")
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)

            st.markdown(f"**Valor Total do Pedido: R$ {st.session_state.total_pedido_temp:.2f}**")

            ##--- Finalizar Pedido ---
            st.subheader("Finalizar Pedido")
            # 1. Pergunta principal: É para entrega? (Fora do form para ser interativo)
            delivery = st.radio(
                "O pedido é para entrega (delivery)?",
                ["Sim", "Não"],
                horizontal=True,
                key="delivery_option"
            )

            # 2. Se não for entrega, faz uma segunda pergunta (também interativa)
            if delivery == "Não":
                # Usamos o session_state para garantir que a escolha seja lembrada
                if 'tipo_pedido_local_option' not in st.session_state:
                    st.session_state.tipo_pedido_local_option = "Para Retirada" # Valor padrão

                tipo_pedido_local = st.radio(
                    "Qual o tipo do pedido?",
                    ["Para Retirada", "Consumo no Local"],
                    horizontal=True,
                    key="tipo_pedido_local_option"
                )

            # 3. O formulário para finalizar o pedido
            with st.form("form_finalizar_pedido"):
                
                # Lógica para definir qual informação de 'endereço' será salva
                if delivery == "Sim":
                    endereco = st.text_input("Endereço de entrega:", placeholder="Rua, número, bairro...")
                else:
                    # O valor vem da segunda pergunta que fizemos
                    endereco = st.session_state.tipo_pedido_local_option

                status_opcao = st.selectbox("Status do Pedido:", ["preparo", "pronto", "entregue"])
                finalizar_button = st.form_submit_button("Salvar Pedido")

                if finalizar_button:
                    # Validação para garantir que o endereço não está vazio se for delivery
                    if delivery == "Sim" and not endereco.strip():
                        st.error("Por favor, insira o endereço de entrega.")
                    else:
                        from model.pedido import Pedido

                        data_hoje = date.today().strftime('%d/%m/%Y')
                        delivery_bool = True if delivery == "Sim" else False
                        total = float(st.session_state.total_pedido_temp)

                        novo_pedido = Pedido(
                            status=status_opcao,
                            delivery=str(delivery_bool),
                            endereco=endereco,
                            date=data_hoje,
                            valor_total=total
                        )

                        # Inserir pedido no banco
                        PedidoControler.insert_into_pedidos(database.name, novo_pedido)

                        # Recuperar o número do pedido inserido
                        pedidos = PedidoControler.search_in_pedidos_all(database.name)
                        numero_pedido = len(pedidos)

                        # Inserir os itens vinculados
                        for item in st.session_state.itens_pedido_temp:
                            for _ in range(item["quantidade"]):
                                ItemControler.insert_into_itens_pedidos(database.name, (numero_pedido, item["id"]))

                        # Configurar o resumo do pedido ANTES de limpar os estados temporários
                        st.session_state.resumo_pedido = {
                            'numero': numero_pedido,
                            'status': status_opcao,
                            'data': data_hoje,
                            'delivery': 'Sim' if delivery_bool else 'Não',
                            'endereco': endereco,
                            'valor': total,
                            'qtd_itens': len(st.session_state.itens_pedido_temp)
                        }

                        # Marcar que o pedido foi finalizado
                        st.session_state.pedido_finalizado = True

                        # Limpar estados temporários
                        st.session_state.itens_pedido_temp = []
                        st.session_state.total_pedido_temp = 0.0
                        
                        st.rerun()
        else:
            st.info("Nenhum item adicionado ao pedido ainda.")

##Página de pesquisa de pedidos
elif opcao == "🔍 Pesquisar Pedidos":
    st.title("🔍 Pesquisar Pedidos")
    st.markdown("---")
    
    tipo_pesquisa = st.selectbox(
        "Tipo de pesquisa:",
        ["Pedido Único", "Todos os Pedidos", "Atualizar Status"]
    )
    
    if tipo_pesquisa == "Pedido Único":
        indice = st.number_input("Índice do pedido:", min_value=1, step=1)
        if st.button("Buscar Pedido"):
            try:
                resume = ItemControler.search_into_itens_pedidos_id(database.name, indice)
                informacoes_pedido = PedidoControler.search_in_pedidos_id(database.name, indice)
                
                if resume and informacoes_pedido:
                    st.success(f"Pedido {indice} encontrado!")
                    
                    ##Exibir itens do pedido
                    st.subheader("Itens do Pedido")
                    for item in resume:
                        st.write(f"**Tipo:** {item[2]} | **Sabor:** {item[0]} | **Descrição:** {item[3]} | **Preço:** R$ {item[1]}")
                    
                    ##Informações do pedido
                    st.subheader("Informações do Pedido")
                    pedido_info = informacoes_pedido[0]
                    st.write(f"**Status:** {pedido_info[1]}")
                    st.write(f"**Delivery:** {pedido_info[2]}")
                    st.write(f"**Endereço:** {pedido_info[3]}")
                    st.write(f"**Data:** {pedido_info[4]}")
                    st.write(f"**Valor:** R$ {pedido_info[5]}")
                else:
                    st.error("Pedido não encontrado!")
            except Exception as e:
                st.error(f"Erro ao buscar pedido: {e}")
    
    elif tipo_pesquisa == "Todos os Pedidos":
        if st.button("Carregar Todos os Pedidos"):
            try:
                pedidos = PedidoControler.search_in_pedidos_all(database.name)
                if pedidos:
                    ##Criar DataFrame para exibir em tabela
                    dados_pedidos = []
                    faturamento_total = 0
                    
                    for i, pedido in enumerate(pedidos, 1):
                        endereco = pedido.endereco or 'Não informado'
                        faturamento_total += pedido.valor_total
                        
                        dados_pedidos.append({
                            'Nº': i,
                            'Status': pedido.status,
                            'Delivery': pedido.delivery,
                            'Endereço': endereco,
                            'Data': pedido.date,
                            'Valor': f"R$ {pedido.valor_total:.2f}"
                        })
                    
                    df = pd.DataFrame(dados_pedidos)
                    st.dataframe(df, use_container_width=True)
                    
                    st.success(f"**Faturamento Total: R$ {faturamento_total:.2f}**")
                else:
                    st.warning("Nenhum pedido encontrado!")
            except Exception as e:
                st.error(f"Erro ao carregar pedidos: {e}")
    
    elif tipo_pesquisa == "Atualizar Status":
        indice = st.number_input("Índice do pedido para atualizar:", min_value=1, step=1)
        
        if st.button("Carregar Pedido"):
            try:
                resume = ItemControler.search_into_itens_pedidos_id(database.name, indice)
                if resume:
                    st.session_state.pedido_carregado = True
                    st.session_state.indice_pedido = indice
                    st.session_state.resume_pedido = resume
                    
                    informacoes_pedido = PedidoControler.search_in_pedidos_id(database.name, indice)[0]
                    st.session_state.info_pedido = informacoes_pedido
                else:
                    st.error("Pedido não encontrado!")
            except Exception as e:
                st.error(f"Erro ao carregar pedido: {e}")
        
        ##Se o pedido foi carregado, mostrar opções de atualização
        if hasattr(st.session_state, 'pedido_carregado') and st.session_state.pedido_carregado:
            st.subheader("Informações do Pedido")
            
            ##Exibir itens
            for item in st.session_state.resume_pedido:
                st.write(f"**Tipo:** {item[2]} | **Sabor:** {item[0]} | **Descrição:** {item[3]} | **Preço:** R$ {item[1]}")
            
            ##Informações atuais
            info = st.session_state.info_pedido
            st.write(f"**Status Atual:** {info[1]}")
            st.write(f"**Delivery:** {info[2]}")
            st.write(f"**Endereço:** {info[3]}")
            st.write(f"**Data:** {info[4]}")
            st.write(f"**Valor:** R$ {info[5]}")
            
            ##Seleção do novo status
            novo_status = st.selectbox(
                "Novo Status:",
                ["Preparo", "Pronto", "Entregue"],
                index=0
            )
            
            if st.button("Atualizar Status"):
                status_map = {"Preparo": 1, "Pronto": 2, "Entregue": 3}
                status_num = status_map[novo_status]
                
                try:
                    resultado = PedidoControler.update_pedido_status(database.name, st.session_state.indice_pedido, status_num)
                    if resultado:
                        st.success(f"Status do Pedido {st.session_state.indice_pedido} atualizado para '{novo_status}' com sucesso!")
                        st.session_state.pedido_carregado = False
                    else:
                        st.error("Erro ao atualizar status!")
                except Exception as e:
                    st.error(f"Erro ao atualizar: {e}")

##Página de relatório
elif opcao == "📊 Relatório":
    st.title("📊 Relatório de Vendas")
    st.markdown("---")
    
    if st.button("Gerar Relatório PDF"):
        try:
            timestamp_atual = str(time.time())
            dados_relatorio = RelatorioControler.preparar_dados_relatorio(database.name)
            relatorio = PDF.gerar_pdf(
                f'Relatorio{timestamp_atual}.pdf', 
                dados_relatorio["pedidos"], 
                dados_relatorio["faturamento_total"]
            )
            
            if relatorio:
                st.success("Relatório gerado com sucesso!")
                st.info(f"Arquivo salvo como: Relatorio{timestamp_atual}.pdf")
            else:
                st.error("Erro ao gerar o relatório.")
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {e}")

##Página de inserção de itens
elif opcao == "🍽️ Inserir Itens Menu":
    st.title("🍽️ Cadastrar Item no Cardápio")
    st.markdown("---")
    
    with st.form("cadastro_item"):
        col1, col2 = st.columns(2)
        
        with col1:
            sabor = st.text_input("Sabor do item *")
            preco = st.number_input("Preço (R$) *", min_value=0.01, step=0.01, format="%.2f")
        
        with col2:
            tipo = st.text_input("Tipo do item *", placeholder="Ex: Pizza, Lanche, Bebida")
            descricao = st.text_area("Descrição do item *")
        
        submitted = st.form_submit_button("Cadastrar Item")
        
        if submitted:
            ##Validações
            if not sabor.strip():
                st.error("Sabor não pode estar vazio!")
            elif not tipo.strip():
                st.error("Tipo não pode estar vazio!")
            elif not descricao.strip():
                st.error("Descrição não pode estar vazia!")
            elif preco <= 0:
                st.error("Preço deve ser maior que zero!")
            else:
                try:
                    ##Criar item
                    dados_item = [sabor.strip(), preco, tipo.strip(), descricao.strip()]
                    novo_item = ItemControler.create_item(dados_item)
                    
                    if novo_item:
                        ##Inserir no banco
                        resultado = ItemControler.insert_into_item(database.name, novo_item)
                        
                        if resultado:
                            st.success(f"Item '{sabor}' cadastrado com sucesso!")
                            st.balloons()
                        else:
                            st.error("Erro ao inserir o item no banco de dados.")
                    else:
                        st.error("Erro ao criar o item. Verifique os dados informados.")
                        
                except Exception as e:
                    st.error(f"Erro inesperado: {e}")
    
    ##Exibir itens do cardápio
    st.markdown("---")
    st.subheader("Itens do Cardápio")
    
    if st.button("Carregar Cardápio"):
        try:
            itens = ItemControler.mostrar_itens_menu(database.name)
            if itens:
                dados_itens = []
                for item in itens:
                    dados_itens.append({
                        'Sabor': item.nome,
                        'Tipo': item.tipo,
                        'Preço': f"R$ {item.preco:.2f}",
                        'Descrição': item.descricao
                    })
                
                df_itens = pd.DataFrame(dados_itens)
                st.dataframe(df_itens, use_container_width=True)
            else:
                st.info("Nenhum item encontrado no cardápio.")
        except Exception as e:
            st.error(f"Erro ao carregar cardápio: {e}")

##Footer
st.sidebar.markdown("---")
st.sidebar.markdown("*Pizza Mais - Seus sonhos tem formato e borda*")