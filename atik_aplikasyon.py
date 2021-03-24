# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 22:51:52 2021

@author: monster
"""

import pandas as pd
import folium
import streamlit as st
import plotly.express as px
from PIL import Image
import geopandas as gpd
from streamlit_folium import folium_static
st.set_page_config(layout="wide",initial_sidebar_state='collapsed')
################################################################################

st.title('Atık Yönetimi ve Nudge')


################################################################################
#Choropleth
st.markdown('## Mahalle Bazında Ağırlıklandırılmış Atık Analizi')
atik = pd.read_excel('12.xls')
atik.Mahalle = atik.Mahalle.str.replace("ç" , "c").str.replace("ş" , "s").str.replace("ğ", "g").str.replace("ı" , "i").str.replace("ö" , "o").str.replace("ü" , "u").str.replace("Ğ" , "G").str.replace("İ" , "I").str.replace("Ç" , "C").str.replace("Ş" , "S").str.replace("Ö" , "O").str.replace("Ü" , "U")
atik.Mahalle.replace('Ivedikkoy Mh.', 'Ivedik Mh.', inplace = True)
atik.Gün.replace([1,2, 3, 4, 5, 6, 7], ['1 Şubat 2021', '2 Şubat 2021', '3 Şubat 2021', '4 Şubat 2021', '5 Şubat 2021', '6 Şubat 2021', '7 Şubat 2021'], inplace = True)
atik['Ağırlıklı Miktar'] = round(atik['Ağırlıklı Miktar'])
mahalle = gpd.read_file('map.shp')
atik = atik.merge(mahalle, how = 'inner', left_on = 'Mahalle', right_on = 'name')
atik_geo = gpd.GeoDataFrame(atik, crs = "EPSG:4326")





row0_0, row0_1 = st.beta_columns([0.3, 0.7])

with row0_0:
    gun = st.selectbox('Tarih seçiniz:', options = list(atik['Gün'].unique()))
    param = st.radio('Parametre seçiniz:', options = ['Toplam Atık', 'Kişi Başına Düşen Atık'])
    ilceler = st.multiselect('Gösterilmeyecek mahalleleri seçiniz:', options=list(atik['Mahalle'].unique()), default = ['Ivedik OSB', 'Ivedik Mh.'])


with row0_1:
    if param == 'Toplam Atık':
        m = folium.Map(location = [39.990429, 32.695547], zoom_start=11, width = '%100', height = '%80')
    #Renk Tonlu Harita
        choropleth = folium.Choropleth(
            geo_data = atik_geo[atik_geo['Gün'] == gun],
            data = atik[atik['Gün'] == gun],
            columns = ['Mahalle', 'Ağırlıklı Miktar'],
            key_on = 'feature.properties.Mahalle',
            fill_color='OrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            bins = 7,
            legend_name='Ağırlıklı Miktar'
            ).add_to(m)

        folium.LayerControl().add_to(m)
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(['Mahalle', 'Ağırlıklı Miktar'], labels=True)
            )
        st.markdown('### Ağırlıklandırılmış Toplam Atık (kg)-Kişi Başına Düşen Atık (kg) Haritası')
        folium_static(m)
    else:
        nufus = pd.DataFrame({'Mahalle':list(atik.Mahalle.unique()), 'Nüfus':[7833, 12032, 16652, 8692, 12355, 8507, 3636, 17341, 8795, 7392, 572, 17526, 2145, 153, 23081, 29499, 17560, 11275, 9960, 18679, 2727,5166, 53914,3771,19053,37243, 27690, 11692, 8848, 7752, 10586, 15927, 7592, 7839, 9406, 4163, 5535, 3599, 4752, 12375,9867, 17519,19669, 29575,16544,12224,7865, 5720, 6336,2843, 961, 1124, 1584 ]})
        atik = atik.merge(nufus, how = 'left', on = 'Mahalle')
        atik_geo = atik_geo.merge(nufus, how = 'left', on = 'Mahalle')
        atik['Kişi Başına Düşen Atık'] = round((atik['Ağırlıklı Miktar'] / atik['Nüfus']),2)
        atik_geo['Kişi Başına Düşen Atık'] = round((atik_geo['Ağırlıklı Miktar'] / atik['Nüfus']),2)
        m1 = folium.Map(location = [39.990429, 32.695547], zoom_start=11)

        #Renk Tonlu Harita
        choropleth = folium.Choropleth(
            geo_data=atik_geo[(atik_geo['Gün'] == gun) & (~atik_geo['Mahalle'].isin(ilceler))],
            data = atik[(atik['Gün'] == gun) & (~atik['Mahalle'].isin(ilceler))],
            columns = ['Mahalle', 'Kişi Başına Düşen Atık'],
            key_on = 'feature.properties.Mahalle',
            fill_color='OrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Kişi Başına Düşen Atık'
            ).add_to(m1)

        folium.LayerControl().add_to(m1)
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(['Mahalle', 'Kişi Başına Düşen Atık'], labels=True)
            )
        st.markdown('### Ağırlıklandırılmış Toplam Atık (kg)-Kişi Başına Düşen Atık (kg) Haritası')
        folium_static(m1)

#######################################################################################################
#Choropleth aggregated

row1_0, row1_1 = st.beta_columns([0.3, 0.7])

with row1_0:
    gunler = st.multiselect('Kümelenecek tarihleri seçiniz:', ['1 Şubat 2021', '2 Şubat 2021', '3 Şubat 2021', '4 Şubat 2021', '5 Şubat 2021', '6 Şubat 2021', '7 Şubat 2021'], ['1 Şubat 2021', '2 Şubat 2021', '3 Şubat 2021', '4 Şubat 2021', '5 Şubat 2021', '6 Şubat 2021', '7 Şubat 2021'])
    stat = st.radio('Hesapalanacak istatistiği seçiniz:', options = ['Toplam', 'Ortalama'])
    bins = st.number_input('İstatistikler kaç kategoriye bölünsün?', min_value = 0, max_value = 10, value = 6)    
    
with row1_1:
    if stat == 'Toplam':
        atik = pd.read_excel('12.xls')
        atik.Mahalle = atik.Mahalle.str.replace("ç" , "c").str.replace("ş" , "s").str.replace("ğ", "g").str.replace("ı" , "i").str.replace("ö" , "o").str.replace("ü" , "u").str.replace("Ğ" , "G").str.replace("İ" , "I").str.replace("Ç" , "C").str.replace("Ş" , "S").str.replace("Ö" , "O").str.replace("Ü" , "U")
        atik.Mahalle.replace('Ivedikkoy Mh.', 'Ivedik Mh.', inplace = True)
        atik.Gün.replace([1,2, 3, 4, 5, 6, 7], ['1 Şubat 2021', '2 Şubat 2021', '3 Şubat 2021', '4 Şubat 2021', '5 Şubat 2021', '6 Şubat 2021', '7 Şubat 2021'], inplace = True)
        mahalle = gpd.read_file('map.shp')
        atik = atik.merge(mahalle, how = 'inner', left_on = 'Mahalle', right_on = 'name')
        atik_geo = gpd.GeoDataFrame(atik, crs = "EPSG:4326")
        toplam_atik = atik[atik['Gün'].isin(gunler)].groupby('Mahalle')['Ağırlıklı Miktar'].sum().to_frame().reset_index()
        toplam_atik = toplam_atik.merge(mahalle, how = 'left', left_on = 'Mahalle', right_on = 'name').rename(columns = {'Ağırlıklı Miktar':'Ağırlıklı Miktar Toplamı'})
        toplam_atik['Ağırlıklı Miktar Toplamı'] = round(toplam_atik['Ağırlıklı Miktar Toplamı'], 2)
        toplam_atik_geo = gpd.GeoDataFrame(toplam_atik, crs = "EPSG:4326")
        
        m2 = folium.Map(location = [39.990429, 32.695547], zoom_start=11)

    #Renk Tonlu Harita
        choropleth = folium.Choropleth(
            geo_data=toplam_atik_geo,
            data = toplam_atik,
            columns = ['Mahalle', 'Ağırlıklı Miktar Toplamı'],
            key_on = 'feature.properties.Mahalle',
            fill_color='OrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            bins = bins,
            legend_name='Ağırlıklı Miktar Toplamı'
            ).add_to(m2)

        folium.LayerControl().add_to(m2)
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(['Mahalle', 'Ağırlıklı Miktar Toplamı'], labels=True)
            )
        st.markdown('### Mahalle Bazlı Tarihe Göre Kümelenmiş Ağırlıklı Toplam Atık Haritası')
        folium_static(m2)
    else:
        atik = pd.read_excel('12.xls')
        atik.Mahalle = atik.Mahalle.str.replace("ç" , "c").str.replace("ş" , "s").str.replace("ğ", "g").str.replace("ı" , "i").str.replace("ö" , "o").str.replace("ü" , "u").str.replace("Ğ" , "G").str.replace("İ" , "I").str.replace("Ç" , "C").str.replace("Ş" , "S").str.replace("Ö" , "O").str.replace("Ü" , "U")
        atik.Mahalle.replace('Ivedikkoy Mh.', 'Ivedik Mh.', inplace = True)
        atik.Gün.replace([1,2, 3, 4, 5, 6, 7], ['1 Şubat 2021', '2 Şubat 2021', '3 Şubat 2021', '4 Şubat 2021', '5 Şubat 2021', '6 Şubat 2021', '7 Şubat 2021'], inplace = True)
        mahalle = gpd.read_file('map.shp')
        atik = atik.merge(mahalle, how = 'inner', left_on = 'Mahalle', right_on = 'name')
        atik_geo = gpd.GeoDataFrame(atik, crs = "EPSG:4326")
        toplam_atik = atik[atik['Gün'].isin(gunler)].groupby('Mahalle')['Ağırlıklı Miktar'].mean().to_frame().reset_index()
        toplam_atik = toplam_atik.merge(mahalle, how = 'left', left_on = 'Mahalle', right_on = 'name').rename(columns = {'Ağırlıklı Miktar':'Ağırlıklı Miktar Ortalaması'})
        toplam_atik['Ağırlıklı Miktar Ortalaması'] = round(toplam_atik['Ağırlıklı Miktar Ortalaması'], 2)
        toplam_atik_geo = gpd.GeoDataFrame(toplam_atik, crs = "EPSG:4326")
        
        m3 = folium.Map(location = [39.990429, 32.695547], zoom_start=11)

    #Renk Tonlu Harita
        choropleth = folium.Choropleth(
            geo_data=toplam_atik_geo,
            data = toplam_atik,
            columns = ['Mahalle', 'Ağırlıklı Miktar Ortalaması'],
            key_on = 'feature.properties.Mahalle',
            fill_color='OrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            bins = bins,
            legend_name='Ağırlıklı Miktar Ortalaması'
            ).add_to(m3)

        folium.LayerControl().add_to(m3)
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(['Mahalle', 'Ağırlıklı Miktar Ortalaması'], labels=True)
            )
        st.markdown('### Mahalle Bazlı Tarihe Göre Kümelenmiş Ağırlıklı Toplam Atık Haritası')
        folium_static(m3)
    
##############################################################################################
st.markdown('## Atık Toplarken Atık Üretmek')
st.markdown('**Not:** Aşağıdaki grafikler Yenimahalle ilçesinde faaliyet gösteren çöp kamyonları verileri baz alınarak üretilmiştir.')

co2 = pd.read_excel('co2.xls')
fig = px.line(co2, x="gun", y="co2", template = 'none', title="Zamansal CO2 Salınımı",
              labels={
                 "gun": "Tarih",
                 "co2": "Co2 Miktarı",
                }, width = 1400)
fig.add_hline(y=co2['co2'].mean(), line_dash="dot")
fig.update_traces(line=dict(color="#20b2aa", width=4)) 
fig.add_annotation(x='2021-02-22', y=10000,
        text="Referans Çizgisi -> Ortalama CO2 Miktarı:" + ' ' +str(round(co2['co2'].mean(),2)),
        showarrow=False,
        font=dict(
     family="sans serif",
     size=16,
     color="#990000"
     ))
             
st.plotly_chart(fig)

    
####################################################################################################
#Heatmap
st.markdown('## Rota Analizi')
co2 = pd.read_excel('co2.xls', 1)
rota = pd.read_excel('rota.xls')
rota_net = rota.groupby(['Rota', 'Plaka', 'Tarih', 'Zaman'])['Net (Atık)'].sum().to_frame().reset_index()
rota_net = rota_net.merge(co2, how = 'left', left_on = ['Plaka', 'Tarih'], right_on = ['plaka', 'Tarih']).dropna()



row3_0, row3_1 = st.beta_columns([1,0.5])

with row3_0:
    rotalar = st.multiselect('Rota(lar) seçiniz:', list(rota_net['Rota'].unique()), default = ['Rota - 1', 'Rota - 2', 'Rota - 3', 'Rota - 4', 'Rota - EK 5', 'Rota - 6', 'Rota - 7', 'Rota - 8', 'Rota - 9', 'Rota - 10'])
    st.markdown('Tarih seçimi için örnek (yıl-ay-gün): 2021-02-01')
    baslangic = st.text_input('Başlangıç tarihi giriniz', value = '2021-02-01')
    bitis = st.text_input('Bitiş tarihi giriniz', value = '2021-02-28')
    zaman = st.multiselect('Zaman seçiniz:', list(rota_net['Zaman'].unique()), ['Gündüz', 'Gece'])

with row3_1:
    image = Image.open('rota.png')
    st.image(image)


row4_0, row4_1 = st.beta_columns([1,1])



with row4_0:
    heat = rota_net[rota_net['Zaman'].isin(zaman) & (rota_net['Rota'].isin(rotalar)) & (rota_net['Tarih'] >= baslangic) & (rota_net['Tarih'] <= bitis)].pivot_table(index = 'Rota', columns = 'Tarih', values = 'co2', aggfunc = 'sum')
    fig = px.imshow(heat, template = 'none', color_continuous_scale = px.colors.sequential.OrRd, 
               labels=dict(x="Tarih", y="Rota", color="Toplam CO2 Salınımı"), height=500)
    fig.update_layout(title='Rota ve Tarih Bazlı CO2 Isı Haritası')
    st.plotly_chart(fig)
    
with row4_1:
    heat = rota_net[rota_net['Zaman'].isin(zaman) & (rota_net['Rota'].isin(rotalar)) & (rota_net['Tarih'] >= baslangic) & (rota_net['Tarih'] <= bitis)].pivot_table(index = 'Rota', columns = 'Tarih', values = 'Net (Atık)', aggfunc = 'sum')
    fig = px.imshow(heat, template = 'none', color_continuous_scale = px.colors.sequential.Bluyl, 
               labels=dict(x="Tarih", y="Rota", color="Toplam Toplanan Atık (kg)"), height=500)
    fig.update_layout(title='Rota ve Tarih Bazlı Toplam Net Atık (kg) Isı Haritası')
    st.plotly_chart(fig)

########################################################################################################
st.markdown('## Araç Bazında Analiz')
st.markdown('#### **Not:** Baloncuk büyüklükleri CO2 salınım miktarı ile orantılıdır.')
co2 = pd.read_excel('co2.xls', 1)
rota = pd.read_excel('rota.xls')
rota_net = rota.groupby(['Rota', 'Plaka', 'Tarih', 'Zaman'])['Net (Atık)'].sum().to_frame().reset_index()
rota_net = rota_net.merge(co2, how = 'left', left_on = ['Plaka', 'Tarih'], right_on = ['plaka', 'Tarih']).dropna()
rota_net.columns =['Rota', 'Araç', 'Tarih', 'Zaman', 'Net (Atık)', 'gun', 'plaka', 'km','co2']
arac = []
for i in range(1,33):
    arac.append('Araç' + ' ' + str(i))
rota_net['Araç'] = rota_net['Araç'].replace(list(rota_net['Araç'].unique()), arac)
araclar = {'Araç 1':'#F5B7B1'}
colors = ['#F5B7B1', '#D2B4DE', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF', '#FF00FF', '#808080', '#800000',
         '#808000', '#E6E6FA', '#800080', '#008080', '#000080', '#B22222', '#F08080', '#FF8C00', '#FFD700', '#F0E68C',
         '#9ACD32', '#008000', '#00FA9A', '#20B2AA', '#00CED1', '#5F9EA0', '#4B0082', '#FF1493', '#FAEBD7', '#BC8F8F',
         '#708090', '#D2691E']
for i in range(32):
    araclar['Araç ' + str(i)] = colors[i]
row5_0, row5_1 = st.beta_columns([1, 1])

with row5_0:
    tarihh = st.text_input('Analiz etmek istediğiniz günü seçiniz:', value = '2021-02-01')
    fig2 = px.scatter(rota_net[rota_net['Tarih'] == tarihh], x="km", y="Net (Atık)", color = 'Araç', size = 'co2', range_y = [0, 38000],
                range_x = [0, 205],
                template = 'none',
                labels={
                     "km": "Katedilen Mesafe (km)",
                     "Net (Atık)": "Toplanan Net Atık Miktarı (kg)",
                 },
                color_discrete_map = araclar)
    fig2.add_annotation(x=157, y=35000,
            text="Toplam Katedilen Mesafe(km):" + str(round(rota_net[rota_net['Tarih'] == tarihh]['km'].sum(),2)),
            showarrow=False,
            font=dict(
            size=13,
            color="Black"
            )
        )
    fig2.add_annotation(x=157, y=33000,
            text="Toplam Co2 Salınımı:" + str(round(rota_net[rota_net['Tarih'] == tarihh]['co2'].sum(),2)),
            showarrow=False,
            font=dict(
            size=13,
            color="Black"
            )
        )
    fig2.add_annotation(x=157, y=31000,
            text="Toplam Toplanan Atık(kg):" + str(round(rota_net[rota_net['Tarih'] == tarihh]['Net (Atık)'].sum(),2)),
            showarrow=False,
            font=dict(
            size=13,
            color="Black"
            )
        )
    st.plotly_chart(fig2)
with row5_1:
    tarihh1 = st.text_input('Kıyaslamak istediğiniz günü seçiniz:', value = '2021-02-02')
    fig2 = px.scatter(rota_net[rota_net['Tarih'] == tarihh1], x="km", y="Net (Atık)", color = 'Araç', size = 'co2', range_y = [0, 38000],
                range_x = [0, 205],
                template = 'none',
                labels={
                     "km": "Katedilen Mesafe (km)",
                     "Net (Atık)": "Toplanan Net Atık Miktarı (kg)",
                 },
                color_discrete_map = araclar)
    fig2.add_annotation(x=157, y=35000,
            text="Toplam Katedilen Mesafe(km):" + str(round(rota_net[rota_net['Tarih'] == tarihh1]['km'].sum(),2)),
            showarrow=False,
            font=dict(
            size=13,
            color="Black"
            )
        )
    fig2.add_annotation(x=157, y=33000,
            text="Toplam Co2 Salınımı:" + str(round(rota_net[rota_net['Tarih'] == tarihh1]['co2'].sum(),2)),
            showarrow=False,
            font=dict(
            size=13,
            color="Black"
            )
        )
    fig2.add_annotation(x=157, y=31000,
            text="Toplam Toplanan Atık(kg):" + str(round(rota_net[rota_net['Tarih'] == tarihh1]['Net (Atık)'].sum(),2)),
            showarrow=False,
            font=dict(
            size=13,
            color="Black"
            )
        )
    st.plotly_chart(fig2)