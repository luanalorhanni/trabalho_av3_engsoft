#Necessário para realizar import em python
import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from controler.itemControler import ItemControler

class Janela3:
    def mostrar_janela3(database_name: str):
        print('------Cadastrar Item no Cardápio--------')
        
        try:
            # Coleta das informações do item
            sabor = input('Sabor do item: ').strip()
            if not sabor:
                print('Sabor não pode estar vazio. Retornando ao menu.')
                return
            
            # Validação do preço
            try:
                preco = float(input('Preço (R$): ').replace(',', '.'))
                if preco <= 0:
                    print('Preço deve ser maior que zero. Retornando ao menu.')
                    return
            except ValueError:
                print('Preço inválido. Retornando ao menu.')
                return
            
            tipo = input('Tipo do item (ex: Pizza, Lanche, Bebida): ').strip()
            if not tipo:
                print('Tipo não pode estar vazio. Retornando ao menu.')
                return
            
            descricao = input('Descrição do item: ').strip()
            if not descricao:
                print('Descrição não pode estar vazia. Retornando ao menu.')
                return
            
            # Confirmação antes de inserir
            print(f'\n--- Confirmação dos dados ---')
            print(f'Sabor: {sabor}')
            print(f'Preço: R$ {preco:.2f}')
            print(f'Tipo: {tipo}')
            print(f'Descrição: {descricao}')
            
            confirmacao = input('\nConfirma o cadastro? (s/n): ').strip().lower()
            
            if confirmacao in ['s', 'sim', 'y', 'yes']:
                # Criação do item usando o método create_item
                dados_item = [sabor, preco, tipo, descricao]
                novo_item = ItemControler.create_item(dados_item)
                
                if novo_item:
                    # Inserção no banco de dados
                    resultado = ItemControler.insert_into_item(database_name, novo_item)
                    
                    if resultado:
                        print(f'\nItem "{sabor}" cadastrado com sucesso!')
                    else:
                        print('\nErro ao inserir o item no banco de dados.')
                else:
                    print('\nErro ao criar o item. Verifique os dados informados.')
            else:
                print('\nCadastro cancelado.')
                
        except KeyboardInterrupt:
            print('\nOperação cancelada pelo usuário.')
        except Exception as e:
            print(f'\nErro inesperado: {e}')
        
        print('Voltando ao menu inicial\n')