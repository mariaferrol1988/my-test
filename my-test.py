# Librerías
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from sklearn.linear_model import LinearRegression


# Funciones ------------------------------------------------------------------------
@st.cache(suppress_st_warning=True,show_spinner=False)
# Lectura de df
def read_df(dfx,cmp,sp,cols):
    df0 = pd.read_csv(dfx,compression = cmp, sep = sp, usecols = cols)
    return df0 

# Resetear nombres de columnas
def reset_columns(df):
    df.columns = ['_'.join(col) for col in df.columns.values]
    return df

# Función para hacer groupby y sumar - Necesito esto?
#def group_perc(dfx,var1,var2,var3,cod1):
#    df0 = (df.groupby([var1,var2])[var3].count() / df.groupby([var1])[var3].count() *100).reset_index()
#    return df0[df0[var2] ==cod1]

# Función para hacer groupby y la media u otra función - Necesito esto?
#def group_func(dfx,var1,var2,func):
#    df0 = df.groupby(var1)[var2].agg([func]).reset_index()
#    return df0

# Función para definir dummies modelo (ausencia del atributo seleccionado en el cuestionario)
def define_var_no(var,word):
    if word in var:
        return 0
    else:
        return 1

# Devolver el restulado de modelo (ausencia atributo)
def define_var_yes(var,word):
    if word in var:
        return 1
    else:
        return 0

# Devolver el restulado de modelo (presencia atributo)
def my_result(x):
    if x < 5.5:
        return 'Tu felicidad estimada es ' + str(round(float(x),2)) + ' sobre 10. Eso significa que estás por debajo de la media.'
    elif x > 8.5:
        return 'Tu felicidad estimada es ' + str(round(float(x),2)) +' sobre 10. Enhorabuena, eso significa que estás por encima de la media.'
    else:
        return 'Tu felicidad estimada es ' + str(round(float(x),2)) + ' sobre 10. Eso significa que estás en la media.'

# ----------------------------------------------------------------------------------

# Slider cuestionario --------------------------------------------------------------    
    
st.sidebar.title("Bienvenido al test :smile:")
st.sidebar.markdown("Contesta a las siguientes para saber tu puntuación!")

estadosalud = st.sidebar.selectbox('¿Cómo valorarías tu salud en general?', \
                                   ('Muy buena', 'Buena', 'Regular', 'Mala','Muy mala'))
salud_dic = {'Muy buena':1, 'Buena':2, 'Regular':3, 'Mala':4,'Muy mala':5}
chronicdis = st.sidebar.selectbox('¿Tienes alguna enfermedad o condición crónica?',
                                ('Sí','No','Prefiero no revelarlo :)'))
limitacion = st.sidebar.selectbox("¿Te has visto limitado en tu vida diaria por motivos de salud en los últimos 6 meses?",('No, para nada', 'Sí, pero sólo levemente','Sí, me he visto muy limitado :('))
economíahogar = st.sidebar.selectbox('¿Qué nivel de dificultad encuentras para llegar a fin de mes?' \
                                     ,('Muy difícil','Difícil','Más bien difícil',
                                       'Más bien fácil', 'Fácil','Muy fácil'))
econ_dic = {'Muy difícil':1, 'Difícil':2, 'Más bien difícil':3, 'Más bien fácil':4, 'Fácil':5, 'Muy fácil':6}
gastoshogar = st.sidebar.selectbox("Por último puedes decirme cuánto te suponen los gastos de vivienda",
                                ("El impacto es bajo","El impacto es medio","El impacto es alto"))
priv_mat = st.sidebar.multiselect('¿Has tenido problemas económicos que te impidieran permitirte alguna de las siguientes cosas?',
                                ("Acceder a interet","Realizar actividades de ocio","Salir con amigos", \
                                 "Gastar dinero en lo que me gusta","Comprar calzado", "Comprar ropa"))
renta = st.sidebar.number_input("¿Podrías decirme tu renta anual?", -55000, 150000,0)


# Datasets ------------------------------------------------------------------------

model = read_df('https://raw.githubusercontent.com/mariaferrol1988/TFM_MasterDataSciences/master/Notebooks/Files/dataset_modelo.csv', None ,';', None)
model['LifeSatisfaction_int'] = model['LifeSatisfaction2'].astype(int) # Nota, meter esto directamente en el modelo o en una función
df_visualization2 = read_df('https://raw.githubusercontent.com/mariaferrol1988/TFM_MasterDataSciences/master/Notebooks/Files/visualizationV2.csv', None ,';', None)
df_corr = read_df('https://raw.githubusercontent.com/mariaferrol1988/TFM_MasterDataSciences/master/Notebooks/Files/correlations.csv', None ,';', None)

# ----------------------------------------------------------------------------------

# Modelo cálculo puntuaciones-------------------------------------------------------

## Resultados almacenados en un dataframe
## df_qnr
df_qnr = pd.DataFrame({'vhRentaa': [renta],
                      'HousingCost_HighImpactHH':[define_var_yes(gastoshogar,'El impacto es alto')], 
                      'CrConditions_YChronic':[define_var_yes(chronicdis,'Sí')],
                      'HLimitations_SerLimited':[define_var_yes(limitacion,'Sí, me he visto muy limitado :(')], 
                      'MDInternet_Yes':[define_var_no(priv_mat,'Acceder a interet')] ,
                      'MDSelf_Yes':[define_var_no(priv_mat,'Gastar dinero en lo que me gusta')],
                      'MDLeisure_Yes':[define_var_no(priv_mat,'Realizar actividades de ocio')],
                      'MDFriends_Yes':[define_var_no(priv_mat,'Salir con amigos')],
                      'MDShoes_Yes':[define_var_no(priv_mat,'Comprar calzado')], 
                      'MDClothes_Yes':[define_var_no(priv_mat,'Comprar ropa')], 
                      'CHealth':[salud_dic[estadosalud]],  
                      'AREMonth':[econ_dic[economíahogar]],
                      'CHealth_D':[estadosalud],  
                      'AREMonth_D':[economíahogar]})
    
## Variables modelo
X = model[['vhRentaa','HousingCost_HighImpactHH','CrConditions_YChronic','HLimitations_SerLimited', 'MDInternet_Yes',
     'MDSelf_Yes', 'MDLeisure_Yes',  'MDFriends_Yes', 'MDShoes_Yes', 'MDClothes_Yes','CHealth','AREMonth']]
y = model['LifeSatisfaction2']

## Modelo
reg = LinearRegression()
reg.fit(X, y)
prediction =reg.predict(df_qnr[['vhRentaa','HousingCost_HighImpactHH','CrConditions_YChronic','HLimitations_SerLimited', 'MDInternet_Yes',
     'MDSelf_Yes', 'MDLeisure_Yes',  'MDFriends_Yes', 'MDShoes_Yes', 'MDClothes_Yes','CHealth','AREMonth']])

# ----------------------------------------------------------------------------------

# Charts ---------------------------------------------------------------------------

#### df distribución + almacenamiento predicciones persona

df13_18grouped = model.groupby(['Year','LifeSatisfaction0'])['Weight'].sum().reset_index()
dfpred = pd.DataFrame({'Person':['Tu felicidad estimada'],'value':[float(prediction)],'point':[500000]})

#### histrograma felicidad con observaciones reales 2013 y 2018

hist_happiness = alt.Chart(df13_18grouped).mark_area(
    opacity=0.5,
    interpolate='step'
).encode(
    x = alt.X('LifeSatisfaction0:Q', # Cambiar en nombre de la variable
              bin=alt.Bin(maxbins=100), 
              title = 'Felicidad',
              axis=alt.Axis(values= [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])),
    y = alt.Y('Weight', # Cambiar el nombre
              stack=None,
              axis = alt.Axis(format =',.2s'),
              title = 'Individuos'),
    tooltip=[alt.Tooltip('LifeSatisfaction0', title = 'Nivel de felicidad'),
             alt.Tooltip('Weight', title = 'Número de personas',format=',.2s')]
).properties(
    width=550,
    height=300
)

#### Predicción sobre la felicidd del individuo en punto / ver otras opciones

pred_point = alt.Chart(dfpred).mark_circle(color = 'black', size = 50).encode(
    alt.X('value'),
    alt.Y('point'),
    tooltip=[alt.Tooltip('value', title = 'Tu nivel de felicidad',format=',.2s')]
).properties(
    width=550,
    height=300
)    

#### Texto de la predicción

pred_text = alt.Chart(dfpred).mark_text(dy=-15, color='black', size = 12).encode(
        alt.X('value'),
        alt.Y('point'),
        text=alt.Text('Person:N'))

happines_histogram = alt.layer(
    hist_happiness, pred_point, pred_text
).properties(
    width=600, height=300
).configure_view(
    strokeWidth=0
)

## Introducción----------------------------------------------------------------------  

#### df felicidad

df_happiness = df_visualization2.groupby(['Year','Quintiles'])['Individuos_quintiles'].mean().reset_index()

#### Filtro
nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['Year'], empty='none')

#### Gráfico felicidad por quintiles
line_quintile = alt.Chart(df_happiness).mark_line(interpolate = 'monotone').encode(
    alt.X('Year:O', title = 'Año',
          axis=alt.Axis(values= [2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018])),
    alt.Y('sum(Individuos_quintiles):Q', 
          title = 'Individuos', 
          axis = alt.Axis(format =',.2s'),
          scale=alt.Scale(domain=[6000000, 12000000])),
    color='Quintiles'
).properties(
    height = 300,
    width = 600
)


selectors = alt.Chart(df_happiness).mark_point().encode(
    x='Year:N',
    opacity=alt.value(0),
).add_selection(
    nearest
)

# Puntos a mostrar
points_quintiles = line_quintile.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

# Texto a mostrar 
text_quintiles = line_quintile.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest,'sum(Individuos_quintiles):Q', alt.value(' '), format=',.2s')
)

# Regla para el seletor
rules_quintiles = alt.Chart(df_happiness).mark_rule(color='gray').encode(
    x='Year:N',
).transform_filter(
    nearest
)

# Put the five layers into a chart and bind the data
happines_distribution = alt.layer(
    line_quintile, selectors, points_quintiles, rules_quintiles, text_quintiles
).properties(
    width=600, height=300
).configure_view(
    strokeWidth=0
)


## Grid de correlaciones  ----------------------------------------------------  

#### base con selección de variables a mostrar (Top 15 variables por correlación con la felicidad

base_corr = alt.Chart(df_corr).encode(
        alt.Y('variable_2:N', 
              title = None),
        alt.X('variable_1:N',
             title = None)
).transform_filter(
    alt.FieldOneOfPredicate(field= 'variable_1', oneOf=['Felicidad','Vacaciones_Sí', 'Ocio en general Sí', 
                                                     'Gasto en uno mismo Sí','"Colchón" económico Sí', 
                                                     'Ocio con amigos Sí','Compra de ropa Sí',
                                                     'Impacto medio coste vivienda','Limitaciones físicas No',
                                                     'Acceso a internet Sí','Carencia Material Severa No',
                                                     'Calefacción Sí','Riesgo de pobreza No', 
                                                     'Compra de zapatos Sí','Ordenador Sí','Enfermedades Crónicas No'])
).transform_filter(
    alt.FieldOneOfPredicate(field= 'variable_2', oneOf=['Felicidad','Vacaciones_Sí', 'Ocio en general Sí', 
                                                     'Gasto en uno mismo Sí','"Colchón" económico Sí', 
                                                     'Ocio con amigos Sí','Compra de ropa Sí',
                                                     'Impacto medio coste vivienda','Limitaciones físicas No',
                                                     'Acceso a internet Sí','Carencia Material Severa No',
                                                     'Calefacción Sí','Riesgo de pobreza No', 
                                                     'Compra de zapatos Sí','Ordenador Sí','Enfermedades Crónicas No'])
).properties(
    height = 650,
    width = 700)

#### Gráfico correlaciones

correlations = base_corr.mark_rect().encode(
    alt.Color('correlation_label:Q', title = 'Correlación')
)


#### Correlaciones en texto
text_corr = base_corr.mark_text().encode(
    text='correlation_label',
    color=alt.condition(
        alt.datum.correlation_label > 0.4, 
        alt.value('white'),
        alt.value('black')
    )
)


## Renta ----------------------------------------------------------------------

## Evolución por factores-------------------------------------------------------------------  

#### Selector de intervalo

select_int = alt.selection(type="interval",encodings=["x"])

#### Gráfico de factores

bar_factors = alt.Chart(df_visualization2).mark_bar(size = 25).encode(
    alt.X('condiciones:N',
         title = None,
         axis = alt.Axis(labelAngle = -45.)),
    alt.Y('mean(Ind_condiciones):Q', 
          title = 'Individuos',
          scale = alt.Scale(domain=[0, 50000000]),
          axis = alt.Axis(format = ',.2s')),
    tooltip='mean(Individuos):Q',
).transform_filter(
    (alt.datum.condiciones_posneg13 != 'Negativo-13') & (alt.datum.condiciones_posneg13 != 'Positivo-13') &
    (alt.datum.condiciones_name != 'Situación Laboral') & (alt.datum.condiciones_posneg == 'Positivo') &
    (alt.datum.condiciones_name != 'Estudios')
).properties(
    width=500,
    height = 150
).transform_filter(
    select_int
)

#### Gráfico de evolución de quintiles

line_quintile2 = alt.Chart(df_visualization2).mark_line(interpolate = 'monotone').encode(
    alt.X('Year:N',
         title = 'Año'),
    alt.Y('mean(Individuos_quintiles):Q',
          title = 'Individuos',
          axis = alt.Axis(format =',.2s'),
          scale=alt.Scale(domain=[6000000, 12000000])),
    alt.Color('Quintiles',
              legend = alt.Legend(title = 'Quintiles'))
).properties(
    width=500,
    height = 250,
    selection=select_int
)

# Chart combinado de factores y evolución
evol_factors = alt.vconcat(line_quintile2, bar_factors,
           resolve = alt.Resolve(scale = alt.LegendResolveMap(color = alt.ResolveMode('independent')))
           ).configure_view(
    strokeWidth=0
)


# Contenido-------------------------------------------------------------------------

## Introducción----------------------------------------------------------------------

st.title('Prediciendo la felicidad')
st.subheader('Una reconstrucción de la felicidad en España durante los últimos 10 años')
st.markdown(str(my_result(prediction)) + ' Evidentemente eso no quiere decir que tú te sientas así, simplemente es la puntuación más probable para alguien de tus características teniendo en cuenta la puntuación del resto de la población.' )
st.markdown('Puedes cambiar las respuestas del cuestionario para hacerte una idea de cómo impactan las condiciones de vida en la felicidad de las personas.')

st.markdown('**Distribución de la felicidad observada en España 2018 & 2019**')
happines_histogram 
 
st.subheader('La evolución de la felicidad')
st.markdown('La felicidad estimada por quintiles muestra una mayor proporción de personas en quintiles inferiores de los años2012 a 2014, mientras que la tendencia se invierte posteriormente, para acabar predominando el número de personas de los quintiles superiores')

st.markdown('**Evolución de la felicidad estimada por quintiles 2008 a 2018**')
happines_distribution

st.subheader('¿A qué se debe esto?')
st.markdown('En la práctica hay muchos factores que impactan en la felicidad de las personas, como la amistad, la salud, o las condiciones económicas. Este modelo utiliza información sobre las condiones de vida, por lo que su fluctuación en el paso del tiempo afecta a las predicciones, así la posibilidad de irse de vacaciones o tener disponible un colchón económico son variables que impactan positivamente en el nivel de felicidad de los individuos.')

# Correlaciones

st.markdown('**Top 15 factores por correlación positiva con la felicidad**')
correlations + text_corr

st.markdown('En este sentido, el mapa de correlaciones, muestra que existe mayor correlación con variables más relacionados con la satisfacción de necesidades sociales y de ocio que con otras más relacionadas con necesidades básicas.')


st.subheader('Entonces, ¿De dónde vienen los cambios?')
st.markdown('Es dificil estimar una única razón por la que un año recibe una estimación más alta que otra, aunque en este sentido, en el gráfico de debajo se que podemos observar cómo tanto la posibilidad de irse de vacaciones o tener ese colchón económico son las condiciones que más varían. Por otro lado otras condiciones como la salud tienden a mantenerse más estables.')

st.markdown('**La evolución de las condiciones de vida**')
evol_factors
