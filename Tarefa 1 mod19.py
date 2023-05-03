#Imports
import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from PIL                 import Image
from io                  import BytesIO


@st.cache_data(show_spinner=True)
def ler_dados(arquivo):
        try:
                return pd.read_csv(arquivo, sep=';')
        except:
               return pd.read_excel(arquivo)

@st.cache_resource
def filtro_multiplo(relatorio, col, selecao):
        if 'Todos' in selecao:
                return relatorio
        else:
                return relatorio[relatorio[col].isin(selecao)].reset_index(drop=True)

@st.cache_resource
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output)
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def main():
        st.set_page_config(page_title = 'Bank Telemarketing',
                                page_icon = '',
                                layout="wide",
                                initial_sidebar_state='expanded')
                        

        st.title('Análise de telemarketing') 
        st.subheader('Nessa aplicação estamos fazendo análises de receptividade de telemarketing com dados de clientes de um banco.')
        

        imagem = Image.open(".\img\Bank-Branding.jpg")
        st.sidebar.image(imagem)

        upload = st.sidebar.file_uploader('Faça upload do arquivo:')



        if upload is not None:
                df_raw = ler_dados(upload)
                df = df_raw.copy()

                st.write('## Antes da filtragem')
                st.dataframe(df_raw.head())
                st.write(df_raw.shape)

                st.sidebar.subheader('Faça a filtragem dos dados:')
                
                # Filtros
                with st.sidebar.form(key='filtro'):
                
                #seleciona o tipo de gráfico

                
                        graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))
                        #IDADE
                        idade_maxima = int(df['age'].max())
                        idade_minima = int(df['age'].min())
                        

                        range_idade = st.slider(label=('Selecione a idade'),
                                                        min_value=idade_minima,
                                                        max_value=idade_maxima,
                                                        value=(idade_maxima,idade_minima))
                        
                                
                        #TRABALHO
                        lista_trabalho = df.job.unique().tolist()
                        lista_trabalho.append('Todos')
                        selec_trabalho = st.multiselect('Selecione a profissão:', lista_trabalho, ['Todos'])

                        #ESTADO CIVIL
                        lista_est_civil = df.marital.unique().tolist()
                        lista_est_civil.append('Todos')
                        selec_est_civil = st.multiselect('Selecione o estado Civíl:', lista_est_civil, ['Todos'])

                        #ESCOLARIDADE
                        lista_escola = df.education.unique().tolist()
                        lista_escola.append('Todos')
                        selec_escola = st.multiselect('Selecione a Escolaridade:', lista_escola, ['Todos'])
                                
                        #DEFAULT?
                        lista_default = df.default.unique().tolist()
                        lista_default.append('Todos')
                        selec_default = st.multiselect('É default?', lista_default, ['Todos'])

                        #TEM IMPRESTIMO?
                        lista_emprestimo = df.loan.unique().tolist()
                        lista_emprestimo.append('Todos')
                        selec_emprestimo = st.multiselect('Tem empréstimo?', lista_emprestimo, ['Todos'])

                        #MES DO CONTATO
                        lista_mes = df.month.unique().tolist()
                        lista_mes.append('Todos')
                        selec_mes = st.multiselect('Mês de contato:', lista_mes, ['Todos'])
                                
                        #DIA DA SEMANA
                        lista_dia = df.day_of_week.unique().tolist()
                        lista_dia.append('Todos')
                        selec_dia = st.multiselect('Dia da semana do contato', lista_dia, ['Todos'])
                                
                        df = (df.query('age >= @range_idade[0] and age <= @range_idade[1]')
                                .pipe(filtro_multiplo, 'job', selec_trabalho)
                                .pipe(filtro_multiplo, 'marital', selec_est_civil)
                                .pipe(filtro_multiplo, 'education',selec_escola)
                                .pipe(filtro_multiplo, 'default', selec_default)
                                .pipe(filtro_multiplo, 'loan', selec_emprestimo)
                                .pipe(filtro_multiplo, 'month', selec_mes)
                                .pipe(filtro_multiplo, 'day_of_week', selec_dia)
                                )
                        aplicar = st.form_submit_button(label='Aplicar')


                



                st.write('## Depois da filtragem')
                st.dataframe(df.head())
                st.write(df.shape)

                df_xlsx = to_excel(df)
                st.download_button(label='📥 Download tabela filtrada em EXCEL',
                                data=df_xlsx ,
                                file_name= 'Dados Filtrados.xlsx')
                st.markdown("---")


                # PLOTS    
                fig, ax = plt.subplots(1, 2, figsize = (5,3))

                df_raw_target_perc = df_raw.y.value_counts(normalize = True).to_frame()*100
                df_raw_target_perc = df_raw_target_perc.sort_index()
                
                try:
                        df_target_perc = df.y.value_counts(normalize = True).to_frame()*100
                        df_target_perc = df_target_perc.sort_index()
                except:
                        st.error('Erro no filtro')
                
                # Botões de download dos dados dos gráficos
                col1, col2 = st.columns(2)

                df_xlsx = to_excel(df_raw_target_perc)
                col1.write('### Proporção original')
                col1.write(df_raw_target_perc)
                col1.download_button(label='📥 Download',
                                data=df_xlsx ,
                                file_name= 'df_raw_y.xlsx')
                
                df_xlsx = to_excel(df_target_perc)
                col2.write('### Proporção da tabela com filtros')
                col2.write(df_target_perc)
                col2.download_button(label='📥 Download',
                                data=df_xlsx ,
                                file_name= 'df_y.xlsx')
                st.markdown("---")
        

                st.write('## Proporção de aceite')
                # PLOTS    
                if graph_type == 'Barras':
                        sns.barplot(x = df_raw_target_perc.index, 
                                y = 'y',
                                data = df_raw_target_perc, 
                                ax = ax[0])
                        ax[0].bar_label(ax[0].containers[0])
                        ax[0].set_title('Dados brutos',
                                fontweight ="bold")
                
                        sns.barplot(x = df_target_perc.index, 
                                y = 'y', 
                                data = df_target_perc, 
                                ax = ax[1])
                        ax[1].bar_label(ax[1].containers[0])
                        ax[1].set_title('Dados filtrados',
                                fontweight ="bold")
                else:
                        df_raw_target_perc.plot(kind='pie', autopct='%.2f', y='y', ax = ax[0])
                        ax[0].set_title('Dados brutos',
                                fontweight ="bold")
                
                        df_target_perc.plot(kind='pie', autopct='%.2f', y='y', ax = ax[1])
                        ax[1].set_title('Dados filtrados',
                                fontweight ="bold")

                st.pyplot(plt)


















        



if __name__ == '__main__':
        main()