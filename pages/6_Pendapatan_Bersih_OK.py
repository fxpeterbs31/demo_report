import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import locale
locale.setlocale(locale.LC_ALL, 'id_ID')

st.set_page_config(page_title = 'Demo Laporan OK')

st.session_state.general_info_penjualan = False
st.session_state.grafik_penjualan       = False
st.session_state.stats_penjualan        = False
st.session_state.stats_penjualan_nota   = False
st.session_state.penjualan_nota         = False

st.session_state.stats_income_general   = False
st.session_state.plot_income_general    = False
st.session_state.stats_income           = False

def formatrupiah(uang):
    y = str(uang)
    if len(y) <= 3:
        return ('Rp. ' + y)
    else :
        p = y[-3:]
        q = y[:-3]
        return (formatrupiah(q) + '.' + p)
    
def expand_cek_stok(nama_barang):
    li_nama_barang = nama_barang.split(' ')

    if nama_barang.startswith('Iphone'):
        nama_barang = ' '.join(li_nama_barang[:-2])
        memori      = ' '.join(li_nama_barang[-2:])
        li_memori   = memori.split(' ')
        
        rom = 0
        if li_memori[1] == 'GB':
            ram = int(li_memori[0])*1
        elif li_memori[1] == 'TB':
            ram = int(li_memori[0])*1024
    else:
        if '/' in nama_barang:
            nama_barang = ' '.join(li_nama_barang[:-1])
            memori      = li_nama_barang[-1] 
            li_memori   = memori.split('/')
            ram         = int(li_memori[0])
            rom         = int(li_memori[1])
        else:
            nama_barang = ' '.join(li_nama_barang)
            memori      = '' 
            ram = rom   = 0

    return [nama_barang, ram, rom]

def get_dates(year, month):
    # Create a datetime object for the first day of the given month
    start_date = datetime(year, month, 1)
    
    # Calculate the number of days in the given month
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
        
    delta = end_date - start_date
    
    # Generate the list of dates
    dates = [start_date + timedelta(days=i) for i in range(delta.days)]
    
    return dates

df_stok = pd.read_excel('demo_data.xlsx')
df_stok['Nama Barang Clean'] = [
    x.split('(')[0].strip() for x in df_stok['Nama Barang']
]

df_stok['Tanggal Jual'] = pd.to_datetime(df_stok['Tanggal Jual'], errors = 'coerce')

df_stok['tahun_jual'] = df_stok['Tanggal Jual'].dt.year
df_stok['bulan_jual'] = df_stok['Tanggal Jual'].dt.month

_, ctr = st.columns([0.75,9.25])
with ctr:
    st.markdown('# PENDAPATAN BERSIH OK')

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

_, ctr = st.columns([2, 8])
with ctr:
    st.markdown('# KEUNTUNGAN UMUM')

expander_profit_general = st.expander('Estimasi Keuntungan', expanded = True)

df_stok_november = df_stok[
    (df_stok['tahun_jual'] == tahun) & 
    (df_stok['bulan_jual'] == bulan)
]

df_stok_november['Harga'] = df_stok_november['Harga'].str.replace('Rp. ', '').str.replace('.', '').str.replace(',-', '')

df_stok_november['Brand'] = df_stok_november['Nama Barang'].str.split(' ').str[0]
df_stok_november['Harga'] = [0 if x == '' else x for x in df_stok_november['Harga']]
df_stok_november['Nama Barang Clean'] = [
    nama_barang.replace(brand, '').strip() \
    for (nama_barang, brand) in zip(
        df_stok_november['Nama Barang Clean'], 
        df_stok_november['Brand']
    )
]

df_stok_november[['Harga', 'Harga Jual']] = df_stok_november[['Harga', 'Harga Jual']].astype('int64')

df_stok_november_modal = df_stok_november[
    ~df_stok_november['Harga'].isin([0, 1000])
]

df_stok_november_modal['Profit'] = df_stok_november_modal['Harga Jual'] - df_stok_november_modal['Harga']
total_profit = formatrupiah(df_stok_november_modal['Profit'].sum())
expander_profit_general.markdown('### Estimasi Keuntungan Bulan {} {} : :blue[{}]'.format(calendar.month_name[bulan], tahun, total_profit))

if 'show_profit_stats' not in st.session_state:
    st.session_state.show_profit_stats = False

def callback_show_profit_stats():
    st.session_state.show_profit_stats = True

btn_show_profit_stats = expander_profit_general.button('Lihat Detail Keuntungan', on_click = callback_show_profit_stats)
if btn_show_profit_stats or st.session_state.show_profit_stats:
    df_recap_profit = df_stok_november_modal\
        .groupby(['Tanggal Jual'])\
        .agg(total_profit = ('Profit', 'sum'))
    
    df_profit_stats = df_recap_profit.describe()

    # 2. Max
    max_profit = df_profit_stats.loc['max', 'total_profit']
    max_profit_day = df_recap_profit[
        df_recap_profit['total_profit'] == max_profit
    ].index
    if len(max_profit_day) == 1:
        max_profit_day = [x.strftime('%d %B %Y').lstrip('0') for x in max_profit_day][0]
    elif len(max_profit_day) > 1:
        max_profit_day = ', '.join([x.strftime('%d %B %Y').lstrip('0') for x in max_profit_day]).strip()

    max_profit = formatrupiah(int(max_profit))

    # 3. Min
    min_profit = df_profit_stats.loc['min', 'total_profit']
    min_profit_day = df_recap_profit[
        df_recap_profit['total_profit'] == min_profit
    ].index
    if len(min_profit_day) == 1:
        min_profit_day = [x.strftime('%d %B %Y').lstrip('0') for x in min_profit_day][0]
    elif len(min_profit_day) > 1:
        min_profit_day = ', '.join([x.strftime('%d %B %Y').lstrip('0') for x in min_profit_day][0]).strip()
        
    min_profit = formatrupiah(int(min_profit))

    # 4. Mean
    mean_profit = df_profit_stats.loc['mean', 'total_profit']
    mean_profit = formatrupiah(int(mean_profit))

    # 5. Median
    median_profit = df_recap_profit['total_profit'].median()
    median_profit = formatrupiah(int(median_profit))

    expander_profit_general.markdown('##### Rata-rata : :green[{},-]'.format(mean_profit))
    expander_profit_general.markdown('##### Median    : :green[{},-]'.format(median_profit))
    expander_profit_general.markdown('##### Keuntungan Terkecil : :green[{},-] ; Pada Tanggal :green[{}]'.format(min_profit, min_profit_day.lstrip('0')))
    expander_profit_general.markdown('##### Keuntungan Terbesar : :green[{},-] ; Pada Tanggal :green[{}]'.format(max_profit, max_profit_day.lstrip('0')))

    if 'show_profit_plot' not in st.session_state:
        st.session_state.show_profit_plot = False

    def callback_show_profit_plot():
        st.session_state.show_profit_plot = True

    btn_show_profit_plot = expander_profit_general.button('Lihat Persebaran Keuntungan', on_click = callback_show_profit_plot)

    if btn_show_profit_plot or st.session_state.show_profit_plot:
        df_recap_profit = df_recap_profit.reset_index()

        min_date = min(df_stok[
            (df_stok['tahun_jual'] == tahun) & 
            (df_stok['bulan_jual'] == bulan)
        ]['Tanggal Jual'])

        max_date = max(df_stok[
            (df_stok['tahun_jual'] == tahun) & 
            (df_stok['bulan_jual'] == bulan)
        ]['Tanggal Jual'])

        new_idx = pd.DataFrame(data = {
            'Tanggal Jual': pd.date_range(min_date, max_date)
        })

        new_idx['Tanggal Jual'] = pd.to_datetime(new_idx['Tanggal Jual'].dt.strftime('%Y-%m-%d'))

        missing_date = list(new_idx[
            ~new_idx['Tanggal Jual'].isin(df_recap_profit['Tanggal Jual'])
        ]['Tanggal Jual'])

        df_missing_date = pd.DataFrame(data = {
            'Tanggal Jual' : missing_date,
            'total_profit' : 0
        })

        df_recap_profit = pd.concat([df_recap_profit, df_missing_date])\
            .sort_values(by = 'Tanggal Jual')\
            .reset_index(drop = True).rename(columns = {
            'total_profit' : 'Total Profit'
        })

        df_recap_profit['Tanggal Jual'] = df_recap_profit['Tanggal Jual'].dt.strftime('%d-%b').str.lstrip('0')

        fig = go.Figure(
            go.Scatter(
                x = list(df_recap_profit['Tanggal Jual']),
                y = list(df_recap_profit['Total Profit']),
                hovertemplate =
                'Tanggal: <b>%{x}</b>'+
                '<br>' +
                'Untung: <b>%{text}</b><extra></extra>',
                text = [formatrupiah(x) for x in list(df_recap_profit['Total Profit'])],
                showlegend = False
            ),
            layout=dict(
                title=dict(
                    text='Estimasi Pendapatan Bersih Harian Bulan {} {}\n'.format(calendar.month_name[bulan], tahun),
                )
            )
        )

        fig.update_layout(
            font_family="Arial",
            font_color="black",
            title_font_family="Arial",
            title_font_color="black",
            legend_title_font_color="black",
            title_font_size = 24,
            title={
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        expander_profit_general.plotly_chart(fig, use_container_width = True)

profit_brand = df_stok_november_modal\
    .groupby(['Brand'])\
    .agg(Profit = ('Profit', 'sum'))\
    .sort_values(by = 'Profit')\
    .reset_index()

_, ctr = st.columns([1,9])
with ctr:
    st.markdown('# KEUNTUNGAN PER BARANG')

expander_profit_brand = st.expander('Estimasi Keuntungan per Brand HP', expanded = True)

fig = go.Figure(
    go.Bar(
        x = list(profit_brand['Brand']),
        y = list(profit_brand['Profit']),
        hovertemplate =
        'Brand: <b>%{x}</b>'+
        '<br>' +
        'Untung: <b>%{text}</b><extra></extra>',
        text = [formatrupiah(x) for x in list(profit_brand['Profit'])],
        showlegend = False
    ),
    layout=dict(
        title=dict(
            text='Estimasi Pendapatan Bersih per Brand Bulan {} {}\n'.format(calendar.month_name[bulan], tahun),
        )
    )
)

fig.update_layout(
    font_family="Arial",
    font_color="black",
    title_font_family="Arial",
    title_font_color="black",
    legend_title_font_color="black",
    title_font_size = 24,
    title={
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    }
)

expander_profit_brand.plotly_chart(fig, use_container_width = True)

options = ['-- Pilih --'] + list(df_stok_november['Brand'].unique())
options = list(np.sort(options))

brand_select_monthly = expander_profit_brand.selectbox(
    'Pilih Brand',
    options = options,
    key = 'brand_select_monthly'
)

if brand_select_monthly != '-- Pilih --':
    df_stok_november_profit_brand = df_stok_november_modal\
        .groupby(['Brand', 'Tanggal Jual'])\
        .agg(Profit = ('Profit', 'sum'))\
        .reset_index()
    
    df_stok_november_profit_brand_small = df_stok_november_profit_brand[
        df_stok_november_profit_brand['Brand'] == brand_select_monthly
    ]

    min_date = min(df_stok[
        (df_stok['tahun_jual'] == tahun) & 
        (df_stok['bulan_jual'] == bulan)
    ]['Tanggal Jual'])

    max_date = max(df_stok[
        (df_stok['tahun_jual'] == tahun) & 
        (df_stok['bulan_jual'] == bulan)
    ]['Tanggal Jual'])

    new_idx = pd.DataFrame(data = {
        'Tanggal Jual': pd.date_range(min_date, max_date)
    })

    new_idx['Tanggal Jual'] = pd.to_datetime(new_idx['Tanggal Jual'].dt.strftime('%Y-%m-%d'))

    missing_date = list(new_idx[
        ~new_idx['Tanggal Jual'].isin(df_stok_november_profit_brand_small['Tanggal Jual'])
    ]['Tanggal Jual'])

    df_missing_date = pd.DataFrame(data = {
        'Brand' : brand_select_monthly,
        'Tanggal Jual' : missing_date,
        'Profit' : 0
    })

    df_stok_november_profit_brand_small = pd.concat([df_stok_november_profit_brand_small, df_missing_date])\
        .sort_values(by = 'Tanggal Jual')\
        .reset_index(drop = True).rename(columns = {
            'total_profit' : 'Total Profit'
        })

    df_stok_november_profit_brand_small['Tanggal Jual'] = df_stok_november_profit_brand_small['Tanggal Jual'].dt.strftime('%d-%b').str.lstrip('0')

    fig = go.Figure(
        go.Scatter(
            x = list(df_stok_november_profit_brand_small['Tanggal Jual']),
            y = list(df_stok_november_profit_brand_small['Profit']),
            hovertemplate =
            'Tanggal: <b>%{x}</b>'+
            '<br>' +
            'Untung: <b>%{text}</b><extra></extra>',
            text = [formatrupiah(x) for x in list(df_stok_november_profit_brand_small['Profit'])],
            showlegend = False
        ),
        layout=dict(
            title=dict(
                text='Estimasi Pendapatan Bersih Harian {} Bulan {} {}\n'.format(brand_select_monthly, calendar.month_name[bulan], tahun),
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
            'yanchor': 'top'
        }
    )

    expander_profit_brand.plotly_chart(fig, use_container_width = True)

expander_profit_item = st.expander('Estimasi Keuntungan per Barang')

options = ['-- Pilih --'] + list(df_stok_november['Brand'].unique())
options = list(np.sort(options))

brand_select = expander_profit_item.selectbox(
    'Pilih Brand',
    options = options
)

if brand_select != '-- Pilih --':
    df_stok_november_modal_brand = df_stok_november_modal[
        df_stok_november_modal['Brand'] == brand_select
    ]

    df_stok_november_modal_item_profit = df_stok_november_modal_brand.groupby('Nama Barang Clean').agg(Profit = ('Profit', 'sum')).sort_values(by = 'Profit').reset_index()
    df_stok_november_modal_item_profit = df_stok_november_modal_item_profit.rename(columns = {
        'Nama Barang Clean' : 'Nama Barang'
    })
    fig = go.Figure(
        go.Bar(
            x = list(df_stok_november_modal_item_profit['Nama Barang']),
            y = list(df_stok_november_modal_item_profit['Profit']),
            hovertemplate =
            'Nama Barang: <b>%{x}</b>'+
            '<br>' +
            'Untung: <b>%{text}</b><extra></extra>',
            text = [formatrupiah(x) for x in list(df_stok_november_modal_item_profit['Profit'])],
            showlegend = False
        ),
        layout=dict(
            title=dict(
                text='Estimasi Pendapatan Bersih {} Bulan {} {}\n'.format(brand_select, calendar.month_name[bulan], tahun),
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
            'yanchor': 'top'
        }
    )

    expander_profit_item.plotly_chart(fig, use_container_width = True)

    df_nama_barang = df_stok_november_modal_brand[['Nama Barang Clean']].drop_duplicates()
    li_memori = df_nama_barang.apply(lambda x: expand_cek_stok(x['Nama Barang Clean']), axis = 1)
    nama_barang_no_memori = li_memori.str[0]
    ram = li_memori.str[1]
    rom = li_memori.str[2]

    df_nama_barang['RAM'] = ram
    df_nama_barang['ROM'] = rom
    df_nama_barang[['RAM', 'ROM']] = df_nama_barang[['RAM', 'ROM']].astype('int64')

    df_nama_barang['Nama Barang no_memori'] = nama_barang_no_memori
    df_nama_barang = df_nama_barang\
        .sort_values(by = ['Nama Barang no_memori', 'RAM', 'ROM'])
    li_nama_barang = ['-- Pilih --'] + list(df_nama_barang['Nama Barang Clean'])
    
    nama_barang = expander_profit_item.selectbox(
        'Nama Barang',
        options = li_nama_barang
    )

    if nama_barang != '-- Pilih --':
        df_stok_november_modal_brand_item = df_stok_november_modal_brand[
            df_stok_november_modal_brand['Nama Barang Clean'] == nama_barang
        ]

        df_stok_november_modal_brand_item_g = df_stok_november_modal_brand_item\
            .groupby(['Tanggal Jual'])\
            .agg(Profit = ('Profit', 'sum'))\
            .reset_index()
        
        min_date = min(df_stok[
            (df_stok['tahun_jual'] == tahun) & 
            (df_stok['bulan_jual'] == bulan)
        ]['Tanggal Jual'])

        max_date = max(df_stok[
            (df_stok['tahun_jual'] == tahun) & 
            (df_stok['bulan_jual'] == bulan)
        ]['Tanggal Jual'])

        new_idx = pd.DataFrame(data = {
            'Tanggal Jual': pd.date_range(min_date, max_date)
        })

        new_idx['Tanggal Jual'] = pd.to_datetime(new_idx['Tanggal Jual'].dt.strftime('%Y-%m-%d'))

        missing_date = list(new_idx[
            ~new_idx['Tanggal Jual'].isin(df_stok_november_modal_brand_item_g['Tanggal Jual'])
        ]['Tanggal Jual'])

        df_missing_date = pd.DataFrame(data = {
            'Tanggal Jual' : missing_date,
            'Profit' : 0
        })

        df_stok_november_modal_brand_item_g = pd.concat([df_stok_november_modal_brand_item_g, df_missing_date])\
            .sort_values(by = 'Tanggal Jual')\
            .reset_index(drop = True).rename(columns = {
                'total_profit' : 'Total Profit'
            })

        df_stok_november_modal_brand_item_g['Tanggal Jual'] = df_stok_november_modal_brand_item_g['Tanggal Jual'].dt.strftime('%d-%b').str.lstrip('0')

        fig = go.Figure(
            go.Scatter(
                x = list(df_stok_november_modal_brand_item_g['Tanggal Jual']),
                y = list(df_stok_november_modal_brand_item_g['Profit']),
                hovertemplate =
                'Tanggal: <b>%{x}</b>'+
                '<br>' +
                'Untung: <b>%{text}</b><extra></extra>',
                text = [formatrupiah(x) for x in list(df_stok_november_modal_brand_item_g['Profit'])],
                showlegend = False
            ),
            layout=dict(
                title=dict(
                    text='Estimasi Pendapatan Bersih {} {} Bulan {} {}\n'.format(brand_select, nama_barang, calendar.month_name[bulan], tahun),
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
                'yanchor': 'top'
            }
        )

        expander_profit_item.plotly_chart(fig, use_container_width = True)

_, ctr = st.columns([1.5,8.5])
with ctr:
    st.markdown('# KEUNTUNGAN PER HARI')

li_date = ['-- Pilih --'] + [x.strftime('%d %B %Y').lstrip('0') for x in get_dates(tahun, bulan)]
date_input_profit_daily = st.selectbox(
    'Tanggal',
    key = 'tgl_input_daily_brand_profit_2',
    options = li_date
)

expander_general_daily = st.expander('Estimasi Keuntungan Harian', expanded = True)

date_input_daily_general_profit = date_input_profit_daily

if date_input_daily_general_profit != '-- Pilih --':
    date_input_daily_general_profit = pd.to_datetime(datetime.strptime(date_input_daily_general_profit, '%d %B %Y'))

    if date_input_daily_general_profit <= datetime.today():
        if date_input_daily_general_profit.month == bulan and date_input_daily_general_profit.year == tahun:
            df_profit_daily = df_stok_november_modal[
                df_stok_november_modal['Tanggal Jual'] == pd.to_datetime(date_input_daily_general_profit)
            ]
            
            total_profit = formatrupiah(sum(df_profit_daily['Profit']))
            expander_general_daily.markdown('##### Estimasi Total Keuntungan Tanggal {}: {}'.format(date_input_daily_general_profit.strftime('%d %B %Y').lstrip('0'), total_profit))
        else:
            expander_general_daily.markdown('#### Silahkan Pilih Tanggal Pada Periode {} {}'.format(calendar.month_name[bulan], tahun))
    else:
        expander_general_daily.markdown('#### Belum Ada Data Untuk Tanggal {}'.format(date_input_daily_general_profit.strftime('%d %B %Y').lstrip('0')))
else:
    expander_general_daily.markdown('#### Silahkan Pilih Tanggal')

expander_brand_daily = st.expander('Estimasi Keuntungan Brand per Hari')

date_input_daily_brand_profit = date_input_profit_daily

if date_input_daily_brand_profit != '-- Pilih --':
    date_input_daily_brand_profit = pd.to_datetime(datetime.strptime(date_input_daily_brand_profit, '%d %B %Y'))

    if date_input_daily_brand_profit <= datetime.today():
        if date_input_daily_brand_profit.month == bulan and date_input_daily_brand_profit.year == tahun:
            df_stok_november_modal_g_daily = df_stok_november_modal\
                .groupby(['Tanggal Jual', 'Brand'])\
                .agg(Profit = ('Profit', 'sum'))\
                .unstack()\
                .fillna(0)\
                .stack()\
                .astype('int64')\
                .reset_index()
            
            df_profit_daily = df_stok_november_modal_g_daily[
                df_stok_november_modal_g_daily['Tanggal Jual'] == pd.to_datetime(date_input_daily_brand_profit)
            ]
            
            fig = go.Figure(
                go.Bar(
                    x = list(df_profit_daily['Brand']),
                    y = list(df_profit_daily['Profit']),
                    hovertemplate =
                    'Brand: <b>%{x}</b>'+
                    '<br>' +
                    'Untung: <b>%{text}</b><extra></extra>',
                    text = [formatrupiah(x) for x in list(df_profit_daily['Profit'])],
                    showlegend = False
                ),
                layout=dict(
                    title=dict(
                        text='Estimasi Pendapatan Bersih Tanggal {}\n'.format(pd.to_datetime(date_input_daily_brand_profit).strftime('%d %B %Y').lstrip('0')),
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
                    'yanchor': 'top'
                }
            )

            expander_brand_daily.plotly_chart(fig, use_container_width = True)

        else:
            expander_brand_daily.markdown('#### Silahkan Pilih Tanggal Pada Periode {} {}'.format(calendar.month_name[bulan], tahun))
    else:
        expander_brand_daily.markdown('#### Belum Ada Data Untuk Tanggal {}'.format(date_input_daily_brand_profit.strftime('%d %B %Y').lstrip('0')))
else:
    expander_brand_daily.markdown('#### Silahkan Pilih Tanggal')

expander_item_daily = st.expander('Estimasi Keuntungan HP per Hari')

date_input_daily_item_profit = date_input_profit_daily

if date_input_daily_item_profit != '-- Pilih --':
    date_input_daily_item_profit = pd.to_datetime(datetime.strptime(date_input_daily_item_profit, '%d %B %Y'))
    
    if date_input_daily_item_profit <= datetime.today():
        if date_input_daily_item_profit.month == bulan and date_input_daily_item_profit.year == tahun:
            df_stok_november_modal['Nama Barang Brand'] = df_stok_november_modal['Nama Barang'].str.split('(').str[0].str.strip()

            df_stok_november_modal_g_daily = df_stok_november_modal\
                .groupby(['Tanggal Jual', 'Nama Barang Brand'])\
                .agg(
                    Profit = ('Profit', 'sum'), 
                    qty = ('IMEI', 'nunique')
                ).unstack()\
                .fillna(0)\
                .stack()\
                .astype('int64')\
                .reset_index()
            
            df_profit_daily = df_stok_november_modal_g_daily[
                (df_stok_november_modal_g_daily['Tanggal Jual'] == pd.to_datetime(date_input_daily_item_profit)) & 
                (df_stok_november_modal_g_daily['Profit'] > 0)
            ].rename(columns = {
                'Nama Barang Brand' : 'Nama Barang'
            })

            li_memori = df_profit_daily.apply(lambda x: expand_cek_stok(x['Nama Barang']), axis = 1)
            nama_barang_no_memori = li_memori.str[0]
            ram = li_memori.str[1]
            rom = li_memori.str[2]
                
            df_profit_daily['RAM'] = ram
            df_profit_daily['ROM'] = rom
            df_profit_daily[['RAM', 'ROM']] = df_profit_daily[['RAM', 'ROM']].astype('int64')

            df_profit_daily['Nama Barang Clean'] = nama_barang_no_memori
            df_profit_daily = df_profit_daily\
                .sort_values(by = ['Profit', 'Nama Barang Clean', 'RAM', 'ROM'])\
                .tail(10)
            
            fig = go.Figure(
                go.Bar(
                    x = list(df_profit_daily['Nama Barang']),
                    y = list(df_profit_daily['Profit']),
                    hovertemplate =
                    'Nama Barang: <b>%{x}</b>'+
                    '<br>' +
                    'Profit: <b>%{text}</b><extra></extra>',
                    text = [formatrupiah(x) for x in list(df_profit_daily['Profit'])],
                    showlegend = False
                ),
                layout=dict(
                    title=dict(
                        text='Estimasi Pendapatan Bersih Tanggal {}\n'.format(pd.to_datetime(date_input_daily_item_profit).strftime('%d %B %Y').lstrip('0')),
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
                    'yanchor': 'top'
                }
            )

            expander_item_daily.plotly_chart(fig, use_container_width = True)

        else:
            expander_item_daily.markdown('#### Silahkan Pilih Tanggal Pada Periode {} {}'.format(calendar.month_name[bulan], tahun))
    else:
        expander_item_daily.markdown('#### Belum Ada Data Untuk Tanggal {}'.format(date_input_daily_item_profit.strftime('%d %B %Y').lstrip('0')))
else:
    expander_item_daily.markdown('#### Silahkan Pilih Tanggal')

