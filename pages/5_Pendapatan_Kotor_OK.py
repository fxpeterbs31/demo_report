import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import numpy as np
import calendar
import locale
locale.setlocale(locale.LC_ALL, 'id_ID')

st.set_page_config(page_title = 'Demo Laporan OK')

st.session_state.general_info_penjualan = False
st.session_state.grafik_penjualan       = False
st.session_state.stats_penjualan        = False
st.session_state.stats_penjualan_nota   = False
st.session_state.penjualan_nota         = False

st.session_state.show_profit_stats      = False
st.session_state.show_profit_plot       = False

def extract_memory(nama_barang):
    if nama_barang.startswith('Iphone'):
        li_nama_barang = nama_barang.split(' ')
        memori = li_nama_barang[-2]
        satuan = li_nama_barang[-1]

        str_memori = ' '.join([memori, satuan]).strip()

        ram = 0
        if satuan == 'GB':
            rom = int(memori)
        elif satuan == 'TB':
            rom = int(memori)*1024
    else:
        if '/' in nama_barang:
            memori = nama_barang.split(' ')[-1]
            str_memori = memori

            li_memori = memori.split('/')
            ram = int(li_memori[0])
            rom = int(li_memori[1])
        else:
            ram = rom = 0
            str_memori = ''

    return [ram, rom, str_memori]

def formatrupiah(uang):
    y = str(uang)
    if len(y) <= 3:
        return ('Rp. ' + y)
    else :
        p = y[-3:]
        q = y[:-3]
        return (formatrupiah(q) + '.' + p)
    
df_stok = pd.read_excel('demo_data.xlsx')
df_stok['Nama Barang Clean'] = [
    x.split('(')[0].strip() for x in df_stok['Nama Barang']
]

df_stok['Tanggal Jual'] = pd.to_datetime(df_stok['Tanggal Jual'], errors = 'coerce')

df_stok['tahun_jual'] = df_stok['Tanggal Jual'].dt.year
df_stok['bulan_jual'] = df_stok['Tanggal Jual'].dt.month

_, ctr = st.columns([0.75,9.25])
with ctr:
    st.markdown('# PENDAPATAN KOTOR OK')

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

expander_income_general = st.expander('Income Gabungan', expanded = True)

df_stok_november = df_stok[
    (df_stok['tahun_jual'] == tahun) & 
    (df_stok['bulan_jual'] == bulan)
]

df_stok_november[['Harga Jual', 'Nomor Bon']] = df_stok_november[['Harga Jual', 'Nomor Bon']].astype('int64')

income_kotor = formatrupiah(df_stok_november['Harga Jual'].sum())

df_stok_november_total_daily = df_stok_november.groupby(['Tanggal Jual']).agg(total_kotor = ('Harga Jual', 'sum'))
df_stok_november_total_stats = df_stok_november_total_daily.describe()

mean = df_stok_november_total_stats.loc['mean', 'total_kotor']
median = df_stok_november_total_stats.loc['50%', 'total_kotor']
min_kotor = df_stok_november_total_stats.loc['min', 'total_kotor']
max_kotor = df_stok_november_total_stats.loc['max', 'total_kotor']

min_kotor_date = pd.to_datetime(str(df_stok_november_total_daily[
    df_stok_november_total_daily['total_kotor'] == min_kotor
].index.values[0])).strftime('%d %B %Y')

max_kotor_date = pd.to_datetime(str(df_stok_november_total_daily[
    df_stok_november_total_daily['total_kotor'] == max_kotor
].index.values[0])).strftime('%d %B %Y')

expander_income_general.markdown('#### Total Pendapatan Kotor {} {} : :green[{},-]'.format(calendar.month_name[bulan], tahun, income_kotor))

if 'stats_income_general' not in st.session_state:
    st.session_state.stats_income_general = False

def callback_stats_income_general():
    st.session_state.stats_income_general = True

btn_stats_income_general = expander_income_general.button('Lihat Detail Income Gabungan', on_click = callback_stats_income_general)

if btn_stats_income_general or st.session_state.stats_income_general:
    expander_income_general.markdown('##### Rata-rata  : :green[{},-]'.format(formatrupiah(int(mean))))
    expander_income_general.markdown('##### Median     : :green[{},-]'.format(formatrupiah(int(median))))
    expander_income_general.markdown('##### Pendapatan Kotor Terkecil   : :green[{},-] ; Pada Tanggal :green[{}]'.format(formatrupiah(int(min_kotor)), min_kotor_date.lstrip('0')))
    expander_income_general.markdown('##### Pendapatan Kotor Terbesar   : :green[{},-] ; Pada Tanggal :green[{}]'.format(formatrupiah(int(max_kotor)), max_kotor_date.lstrip('0')))

    if 'plot_income_general' not in st.session_state:
        st.session_state.plot_income_general = False

    def callback_plot_income_general():
        st.session_state.plot_income_general = True

    btn_plot_income_general = expander_income_general.button('Lihat Persebaran Income', on_click = callback_plot_income_general)
    if btn_plot_income_general or st.session_state.plot_income_general:
        df_stok_november_total_daily_to_display = df_stok_november_total_daily.copy()
        df_stok_november_total_daily_to_display = df_stok_november_total_daily_to_display.reset_index()
        df_stok_november_total_daily_to_display['Tanggal Jual'] = df_stok_november_total_daily_to_display['Tanggal Jual'].astype('datetime64[ns]')
        df_stok_november_total_daily_to_display['Tanggal Jual'] = df_stok_november_total_daily_to_display['Tanggal Jual'].dt.strftime('%d-%b').str.lstrip('0')

        df_stok_november_total_daily_to_display = df_stok_november_total_daily_to_display.rename(columns = {
            'total_kotor' : 'Total'
        })

        fig = go.Figure(
            go.Scatter(
                x = list(df_stok_november_total_daily_to_display['Tanggal Jual']),
                y = list(df_stok_november_total_daily_to_display['Total']),
                hovertemplate =
                'Tanggal: <b>%{x}</b>'+
                '<br>' +
                'Total: <b>%{text}</b><extra></extra>',
                text = [formatrupiah(x) for x in list(df_stok_november_total_daily_to_display['Total'])],
                showlegend = False,
                line=dict(color="#338237")
            ),
            layout=dict(
                title=dict(
                    text='Pendapatan Kotor Bulan {} {}\n'.format(calendar.month_name[bulan], tahun),
                )
            )
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

        expander_income_general.plotly_chart(fig, use_container_width = True)
