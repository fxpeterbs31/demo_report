import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import locale
locale.setlocale(locale.LC_ALL, 'id_ID')

st.set_page_config(page_title = 'Laporan OK')

st.session_state.general_info_penjualan = False
st.session_state.grafik_penjualan       = False
st.session_state.stats_penjualan        = False
st.session_state.stats_penjualan_nota   = False
st.session_state.penjualan_nota         = False

st.session_state.stats_income_general   = False
st.session_state.plot_income_general    = False
st.session_state.stats_income           = False

st.session_state.show_profit_stats      = False
st.session_state.show_profit_plot       = False

df_stok = pd.read_excel('demo_data.xlsx')
df_stok['Nama Barang Clean'] = [
    x.split('(')[0].strip() for x in df_stok['Nama Barang']
]

df_stok['Tanggal Jual'] = pd.to_datetime(df_stok['Tanggal Jual'], errors = 'coerce')

df_stok['tahun_jual'] = df_stok['Tanggal Jual'].dt.year
df_stok['bulan_jual'] = df_stok['Tanggal Jual'].dt.month

_, ctr, _ = st.columns([3,6,3])
with ctr:
    st.markdown('# USER OK')

col_tahun, col_bulan = st.columns(2)

with col_tahun:
    options = list(df_stok['tahun_jual'].unique())
    options = [int(x) for x in options if pd.isnull(x) == False]
    options = list(np.sort(options))

    tahun = st.selectbox(
        'Tahun',
        options = options
    )

with col_bulan:
    options = list(df_stok['bulan_jual'].unique())
    options = [int(x) for x in options if pd.isnull(x) == False]
    options = list(np.sort(options))

    bulan = st.selectbox(
        'Bulan',
        options = options
    )

df_jual_november = df_stok[
    (df_stok['tahun_jual'] == tahun) & 
    (df_stok['bulan_jual'] == bulan)
]

df_jual_november['User'] = df_jual_november['User'].str.lower().str.title()
df_jual_november['Penjual'] = df_jual_november['Penjual'].str.lower().str.title().str.strip()
df_jual_november = df_jual_november[
    ~df_jual_november['Penjual'].isin(['Brand', ''])
]

df_november_recap_qty = df_jual_november.groupby(['User']).agg(
    Jumlah = ('IMEI', 'count')
).sort_values(by = ['Jumlah'], ascending = False).reset_index()

df_november_recap_bon = df_jual_november.groupby(['User']).agg(
    Jumlah = ('Nomor Bon', 'nunique')
).sort_values(by = ['Jumlah'], ascending = False).reset_index()

df_november_recap_qty['Tipe'] = 'Unit'
df_november_recap_bon['Tipe'] = 'Nota'

df_november_recap = pd.concat([df_november_recap_qty, df_november_recap_bon])
df_november_recap = df_november_recap[
    df_november_recap['User'] != ''
]

df_november_recap_g = df_november_recap.groupby('User').agg(total = ('Jumlah', 'sum')).sort_values(by = 'total', ascending = False).reset_index()

df_november_recap_combine = pd.merge(df_november_recap_g, df_november_recap, on = 'User', how = 'inner')
top_15_unit = df_november_recap_combine[
    df_november_recap_combine['Tipe'] == 'Unit'
]
top_15_nota = df_november_recap_combine[
    df_november_recap_combine['Tipe'] == 'Nota'
]

top_15_unit_user = top_15_unit.sort_values(by = 'Jumlah', ascending = False).head(15)[['User']]
top_15_nota_user = top_15_nota.sort_values(by = 'Jumlah', ascending = False).head(15)['User']

df_top_15_unit = pd.merge(top_15_unit_user, df_november_recap_combine, on = 'User', how = 'inner')
df_top_15_nota = pd.merge(top_15_nota_user, df_november_recap_combine, on = 'User', how = 'inner')

expander_user_nota = st.expander('User OK Berdasarkan Nota yang Digunakan', expanded = True)
fig = px.bar(
    df_top_15_nota,
    x = 'User',
    y = 'Jumlah',
    color = 'Tipe',
    title = 'User vs Nota',
    template = 'none',
    barmode = 'group',
    color_discrete_map = {
        'Unit' : '#FF00FF',
        'Nota' : '#808000'
    }
)

fig.update_layout(
    font_family="Arial",
    font_color="black",
    title_font_family="Arial",
    title_font_color="black",
    legend_title_font_color="black",
    title_font_size = 20,
    title={
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)

fig.update_traces(textfont_size=20, textangle=0, textposition="outside", cliponaxis=False)

expander_user_nota.plotly_chart(fig, use_container_width = True)
expander_user_nota.markdown('#### Notes: Yang Paling Sering Berbelanja di OK Berdasarkan Jumlah Nota: ')

user = df_top_15_nota['User'].unique()

for idx, i in enumerate(user):
    expander_user_nota.write('{}. :red[**{}**]'.format(idx+1, i))

    if idx == 2:
        break

expander_user_qty = st.expander('User OK Berdasarkan Jumlah Unit Terjual', expanded = True)
fig = px.bar(
    df_top_15_unit,
    x = 'User',
    y = 'Jumlah',
    color = 'Tipe',
    title = 'User vs Unit',
    template = 'none',
    barmode = 'group',
    color_discrete_map = {
        'Unit' : '#FF00FF',
        'Nota' : '#808000'
    }
)

fig.update_layout(
    font_family="Arial",
    font_color="black",
    title_font_family="Arial",
    title_font_color="black",
    legend_title_font_color="black",
    title_font_size = 20,
    title={
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)

fig.update_traces(textfont_size=20, textangle=0, textposition="outside", cliponaxis=False)

expander_user_qty.plotly_chart(fig, use_container_width = True)
expander_user_qty.markdown('#### Notes: Yang Paling Sering Berbelanja di OK Berdasarkan Total Barang: ')

user = df_top_15_unit['User'].unique()

for idx, i in enumerate(user):
    expander_user_qty.write('{}. :red[**{}**]'.format(idx+1, i))

    if idx == 2:
        break
