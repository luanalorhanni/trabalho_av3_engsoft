import streamlit as st
import sys
import time
from pathlib import Path
import pandas as pd

# Configuração de paths
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Models
from model.pedido import Pedido
from model.item import Item
from model.database import Database

# Controllers
from controler.pedidoControler import PedidoControler
from controler.itemControler import ItemControler
from controler.databaseControler import DatabaseControler
from controler.relatorioController import RelatorioControler

# Report
from report.relatorio1 import PDF

# Configuração da página
st.set_page_config(
    page_title="Pizza Mais - Sistema de Gestão",
    page_icon="🍕",
    layout="wide"
)

# Inicialização do banco de dados
@st.cache_resource
def init_database():
    database = Database('TESTE.db')
    cursor = DatabaseControler.conect_database(database.name)
    DatabaseControler.create_table_itens(cursor)
    DatabaseControler.create_table_pedidos(cursor)
    DatabaseControler.create_table_itens_pedidos(cursor)
    return database

database = init_database()

# Sidebar para navegação
st.sidebar.title("🍕 Pizza Mais")
st.sidebar.markdown("*Criando Sonhos*")
st.sidebar.markdown("---")

opcao = st.sidebar.selectbox(
    "Escolha uma opção:",
    ["🏠 Início", "📝 Cadastrar Pedido", "🔍 Pesquisar Pedidos", "📊 Relatório", "🍽️ Inserir Itens Menu"]
)

# Página principal
if opcao == "🏠 Início":
    st.title("🍕 Pizza Mais - Sistema de Gestão")
    st.markdown("### *Criando Sonhos*")
    st.markdown("**Estabelecimento:** Pizza Ciclano")
    st.markdown("*Seus sonhos tem formato e borda*")
    st.markdown("---")
    
    # Dashboard com métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            pedidos = PedidoControler.search_in_pedidos_all(database.name)
            total_pedidos = len(pedidos) if pedidos else 0
            st.metric("Total de Pedidos", total_pedidos)
        except:
            st.metric("Total de Pedidos", 0)
    
    with col2:
        try:
            faturamento = sum(pedido.valor_total for pedido in pedidos) if pedidos else 0
            st.metric("Faturamento Total", f"R$ {faturamento:.2f}")
        except:
            st.metric("Faturamento Total", "R$ 0,00")
    
    with col3:
        try:
            itens_menu = ItemControler.search_in_itens_all(database.name)
            total_itens = len(itens_menu) if itens_menu else 0
            st.metric("Itens no Menu", total_itens)
        except:
            st.metric("Itens no Menu", 0)

# Página de cadastro de pedidos
elif opcao == "📝 Cadastrar Pedido":
    st.title("📝 Cadastrar Novo Pedido")
    st.markdown("---")
    
    # Aqui você integraria com a lógica da Janela1
    st.info("Esta funcionalidade seria integrada com a lógica da Janela1")
    st.markdown("Para implementar completamente, precisaríamos adaptar a lógica da `Janela1.mostrar_janela1()` para Streamlit")

# Página de pesquisa de pedidos
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
                    
                    # Exibir itens do pedido
                    st.subheader("Itens do Pedido")
                    for item in resume:
                        st.write(f"**Tipo:** {item[2]} | **Sabor:** {item[0]} | **Descrição:** {item[3]} | **Preço:** R$ {item[1]}")
                    
                    # Informações do pedido
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
                    # Criar DataFrame para exibir em tabela
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
        
        # Se o pedido foi carregado, mostrar opções de atualização
        if hasattr(st.session_state, 'pedido_carregado') and st.session_state.pedido_carregado:
            st.subheader("Informações do Pedido")
            
            # Exibir itens
            for item in st.session_state.resume_pedido:
                st.write(f"**Tipo:** {item[2]} | **Sabor:** {item[0]} | **Descrição:** {item[3]} | **Preço:** R$ {item[1]}")
            
            # Informações atuais
            info = st.session_state.info_pedido
            st.write(f"**Status Atual:** {info[1]}")
            st.write(f"**Delivery:** {info[2]}")
            st.write(f"**Endereço:** {info[3]}")
            st.write(f"**Data:** {info[4]}")
            st.write(f"**Valor:** R$ {info[5]}")
            
            # Seleção do novo status
            novo_status = st.selectbox(
                "Novo Status:",
                ["Preparo", "Pronto", "Entregue"],
                index=0
            )
            
            if st.button("Atualizar Status"):
                status_map = {"Preparo": 1, "Pronto": 2, "Entregue": 3}
                status_num = status_map[novo_status]
                
                try:
                    resultado = PedidoControler.update_pedido_status_id(database.name, st.session_state.indice_pedido, status_num)
                    if resultado:
                        st.success(f"Status do Pedido {st.session_state.indice_pedido} atualizado para '{novo_status}' com sucesso!")
                        st.session_state.pedido_carregado = False
                    else:
                        st.error("Erro ao atualizar status!")
                except Exception as e:
                    st.error(f"Erro ao atualizar: {e}")

# Página de relatório
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

# Página de inserção de itens
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
            # Validações
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
                    # Criar item
                    dados_item = [sabor.strip(), preco, tipo.strip(), descricao.strip()]
                    novo_item = ItemControler.create_item(dados_item)
                    
                    if novo_item:
                        # Inserir no banco
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
    
    # Exibir itens do cardápio
    st.markdown("---")
    st.subheader("Itens do Cardápio")
    
    if st.button("Carregar Cardápio"):
        try:
            itens = ItemControler.search_in_itens_all(database.name)
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

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("*Pizza Ciclano - Seus sonhos tem formato e borda*")