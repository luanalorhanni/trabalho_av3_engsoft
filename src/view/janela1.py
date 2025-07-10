#para pegar a data de hoje
from datetime import date
import time

#Necessário para realizar import em python
import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

#importando os módulos de model
from model.pedido import Pedido

#importando os módulos de controle
from controler.pedidoControler import PedidoControler
from controler.itemControler import ItemControler

#criação da classe janela
class Janela1:
    
    @staticmethod
    def mostrar_janela1(database_name: str) -> None:
        """
        View para o usuário utilizar o software
        
        return None
        """
        
        # Loop principal do menu para manter o programa rodando até o usuário decidir sair
        while True:
            # ALTERAÇÃO 1: Menu principal mais claro e objetivo
            print("\n---------- Menu Principal ----------")
            print("1 - Cadastrar Novo Pedido")
            print("0 - Sair do Sistema")
            
            opcao = input("Digite a opção desejada: ")
            
            if opcao == '1':
                # O código de cadastro de pedido começa aqui, pois o usuário já escolheu essa opção
                print('\n---------- Itens Disponíveis ----------\n')
                menu_itens = ItemControler.mostrar_itens_menu(database_name)
                print(f'{menu_itens} \n')
                
                lista_itens = []
                valor_total = 0
                
                print('---------- Cadastrar Pedido ----------\n')
                
                pedidos = PedidoControler.search_in_pedidos_all(database_name)
                numero_pedido = len(pedidos) + 1
                
                # Loop para adicionar itens ao pedido
                while True:
                    item = int(input('Numero do item: '))
                    quantidade = int(input('Quantidade: '))
                    
                    #calculando em tempo de execução o valor do pedido
                    valor_unitario = ItemControler.valor_item(database_name, item)
                    subtotal_item = valor_unitario[0][0] * quantidade
                    print(f"Subtotal do item: R$ {subtotal_item:.2f}")
                    valor_total += subtotal_item
                    
                    # acrescentado o mesmo item várias vezes, de acordo com a quantidade
                    for _ in range(quantidade):
                        lista_itens.append((numero_pedido, item))
                    
                    # ALTERAÇÃO 2: Verificação flexível para 'sim' ou 'não'
                    adicionar_mais = input('Adicionar novo item? (Sim/Nao): ').lower()
                    if adicionar_mais.startswith('n'): # Aceita 'n', 'nao', 'não'
                        break
                
                print('\n---------- Finalizar Pedido ----------\n')
                print(f'Numero do pedido: {numero_pedido}')
                
                # ALTERAÇÃO 2: Verificação flexível para o tipo de entrega
                delivery_input = input('Delivery? (Sim/Nao): ').lower()
                if delivery_input.startswith('s'): # Aceita 's' e 'sim'
                    delivery = True
                    endereco = str(input('Endereco: '))
                elif delivery_input.startswith('n'): # Aceita 'n', 'nao', 'não'
                    delivery = False
                    endereco = "Retirada no local"
                else:
                    print('Opção inválida para delivery. O pedido será cancelado.')
                    continue # Volta para o menu principal
                
                # Tratamento do status do pedido
                status_aux = int(input('Status: 1-Preparo, 2-Pronto, 3-Entregue: '))
                if status_aux == 1:
                    status = 'preparo'
                elif status_aux == 2:
                    status = 'pronto'
                elif status_aux == 3:
                    status = 'entregue'
                else:
                    # Define um status padrão ou cancela, caso a opção seja inválida
                    print("Status inválido. Definido como 'preparo' por padrão.")
                    status = 'preparo'
 
                print(f'\nValor Final: R$ {valor_total:.2f}')
                data_hoje = date.today()
                data_formatada = data_hoje.strftime('%d/%m/%Y')
                
                print(f'Data: {data_formatada}')
                print(f'Endereço de entrega: {endereco}')
                print('Pedido cadastrado com sucesso!')
                
                # Criação e inserção do pedido no banco de dados
                pedido = Pedido(status, str(delivery), endereco, data_formatada, float(valor_total))
                PedidoControler.insert_into_pedidos(database_name, pedido)
                for elem in lista_itens:
                    ItemControler.insert_into_itens_pedidos(database_name, elem)
                
                time.sleep(3) # Pausa para o usuário ver a confirmação

            elif opcao == '0':
                print('\nSaindo do sistema... Até logo!')
                time.sleep(2)
                break # Encerra o loop principal e finaliza o programa
            
            else:
                print("\nOpção inválida! Por favor, tente novamente.")
                time.sleep(2)
