import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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

st.session_state.show_profit_stats      = False
st.session_state.show_profit_plot       = False

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

df_stok = pd.read_excel('demo_data.xlsx')
df_stok['Nama Barang Clean'] = [
    x.split('(')[0].strip() for x in df_stok['Nama Barang']
]
df_stok['Tanggal'] = df_stok['Tanggal'].astype('datetime64[ns]')
df_stok['Tanggal Jual'] = pd.to_datetime(df_stok['Tanggal Jual'], errors = 'coerce')

df_stok['tahun_masuk'] = df_stok['Tanggal'].dt.year
df_stok['bulan_masuk'] = df_stok['Tanggal'].dt.month

df_stok['tahun_jual'] = df_stok['Tanggal Jual'].dt.year
df_stok['bulan_jual'] = df_stok['Tanggal Jual'].dt.month

_, ctr = st.columns([0.125, 9.875])
with ctr:
    st.markdown('# REKAPITULASI KELUAR/MASUK HP')
    
col_tahun, col_bulan = st.columns(2)

with col_tahun:
    options = list(df_stok['tahun_masuk'].unique())
    options = [int(x) for x in options if pd.isnull(x) == False]
    options = list(np.sort(options))

    tahun = st.selectbox(
        'Tahun',
        options = options
    )

with col_bulan:
    options = list(df_stok['bulan_masuk'].unique())
    options = [int(x) for x in options if pd.isnull(x) == False]
    options = list(np.sort(options))

    bulan = st.selectbox(
        'Bulan',
        options = options
    )

_, ctr, _ = st.columns([4,4,3])
with ctr:
    st.markdown('## JAKARTA')
    
expander_keluar_masuk_all = st.expander('Rekapitulasi Keluar/Masuk Barang')
df_masuk_nov = df_stok[
    (df_stok['tahun_masuk'] == tahun) &
    (df_stok['bulan_masuk'] == bulan)
]

df_jual_nov = df_stok[
    (df_stok['tahun_jual'] == tahun) &
    (df_stok['bulan_jual'] == bulan)
]

df_masuk_nov_g = df_masuk_nov\
    .groupby('Tanggal')\
    .agg(count = ('IMEI', 'count'))\
    .reset_index()

df_jual_nov_g = df_jual_nov\
    .groupby('Tanggal Jual')\
    .agg(count = ('IMEI', 'count'))\
    .reset_index()\
    .rename(columns = {
        'Tanggal Jual' : 'Tanggal'
    })

df_masuk_nov_g['Status'] = 'Masuk'
df_jual_nov_g['Status'] = 'Jual'

df_recap = pd.concat([df_masuk_nov_g, df_jual_nov_g])

min_date = min(df_stok[
    (df_stok['Tanggal'].dt.year == tahun) & 
    (df_stok['Tanggal'].dt.month == bulan)
]['Tanggal'])

max_date = max(df_stok[
    (df_stok['Tanggal'].dt.year == tahun) & 
    (df_stok['Tanggal'].dt.month == bulan)
]['Tanggal'])

new_idx = pd.DataFrame(data = {
    'Tanggal': pd.date_range(min_date, max_date)
})

new_idx['Tanggal'] = pd.to_datetime(new_idx['Tanggal'].dt.strftime('%Y-%m-%d'))

missing_date = list(new_idx[
    ~new_idx['Tanggal'].isin(df_recap['Tanggal'])
]['Tanggal'])

df_missing_date_masuk = pd.DataFrame(data = {
    'Tanggal' : missing_date,
    'count' : 0,
    'Status' : 'Masuk'
})

df_missing_date_jual = pd.DataFrame(data = {
    'Tanggal' : missing_date,
    'count' : 0,
    'Status' : 'Jual'
})

df_missing_date = pd.concat([df_missing_date_masuk, df_missing_date_jual])\
    .sort_values(by = 'Tanggal')\
    .reset_index(drop = True)

df_monthly = pd.concat([df_recap, df_missing_date])\
    .reset_index(drop = True)\
    .sort_values(by = ['Tanggal', 'Status'])\
    .set_index(['Tanggal', 'Status'])\
    .unstack()\
    .fillna(0)\
    .astype('int64')\
    .stack()\
    .reset_index()

df_monthly['Tanggal'] = df_monthly['Tanggal'].astype('datetime64[ns]').dt.strftime('%d-%b').str.lstrip('0')
df_monthly = df_monthly.rename(columns = {
    'count' : 'Jumlah'
})

df_keluar_masuk_nov_to_display = df_monthly.copy()

fig = px.line(
    data_frame = df_keluar_masuk_nov_to_display,
    x = 'Tanggal',
    y = 'Jumlah',
    color = 'Status',
    title = 'Rekapitulasi Keluar/Masuk {} {}'.format(calendar.month_name[bulan], tahun),
    template = 'none'
)

fig.update_layout(
    font_family="Arial",
    font_color="black",
    title_font_family="Arial",
    title_font_color="black",
    legend_title_font_color="black",
    title_font_size = 25,
    title={
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)

expander_keluar_masuk_all.plotly_chart(fig, use_container_width = True)

expander_keluar_masuk_daily = st.expander('Rekapitulasi Keluar/Masuk Barang Harian')
tgl_input = expander_keluar_masuk_daily.date_input(
    'Pilih Tanggal',
    key = 'tgl_input',
    value = None
)

if tgl_input is not None:
    if tgl_input.year == tahun and tgl_input.month == bulan:
        df_masuk_nov = df_stok[
            (df_stok['tahun_masuk'] == tahun) &
            (df_stok['bulan_masuk'] == bulan)
        ]

        df_jual_nov = df_stok[
            (df_stok['tahun_jual'] == tahun) &
            (df_stok['bulan_jual'] == bulan)
        ]

        df_masuk_nov_g = df_masuk_nov\
            .groupby(['Tanggal'])\
            .agg(count = ('IMEI', 'count'))\
            .reset_index()

        df_jual_nov_g = df_jual_nov\
            .groupby(['Tanggal Jual'])\
            .agg(count = ('IMEI', 'count'))\
            .reset_index()\
            .rename(columns = {
                'Tanggal Jual' : 'Tanggal'
            })

        df_masuk_nov_g['Status'] = 'Masuk'
        df_jual_nov_g['Status'] = 'Jual'

        df_recap = pd.concat([df_masuk_nov_g, df_jual_nov_g])

        min_date = min(df_stok[
            (df_stok['Tanggal'].dt.year == tahun) & 
            (df_stok['Tanggal'].dt.month == bulan)
        ]['Tanggal'])

        max_date = max(df_stok[
            (df_stok['Tanggal'].dt.year == tahun) & 
            (df_stok['Tanggal'].dt.month == bulan)
        ]['Tanggal'])

        new_idx = pd.DataFrame(data = {
            'Tanggal': pd.date_range(min_date, max_date)
        })

        new_idx['Tanggal'] = pd.to_datetime(new_idx['Tanggal'].dt.strftime('%Y-%m-%d'))

        missing_date = list(new_idx[
            ~new_idx['Tanggal'].isin(df_recap['Tanggal'])
        ]['Tanggal'])

        df_missing_date_masuk = pd.DataFrame(data = {
            'Tanggal' : missing_date,
            'count' : 0,
            'Status' : 'Masuk'
        })

        df_missing_date_jual = pd.DataFrame(data = {
            'Tanggal' : missing_date,
            'count' : 0,
            'Status' : 'Jual'
        })

        df_missing_date = pd.concat([df_missing_date_masuk, df_missing_date_jual])\
            .sort_values(by = 'Tanggal')\
            .reset_index(drop = True)
        
        df_monthly = pd.concat([df_recap, df_missing_date])\
            .reset_index(drop = True)\
            .sort_values(by = ['Tanggal', 'Status'])\
            .set_index(['Tanggal', 'Status'])\
            .unstack(level = 1)\
            .fillna(0)\
            .astype('int64')\
            .stack()\
            .reset_index()

        df_keluar_masuk_nov_daily = df_monthly[
            df_monthly['Tanggal'] == str(tgl_input)   
        ]

        df_keluar_masuk_nov_daily_to_display = df_keluar_masuk_nov_daily.copy()
        df_keluar_masuk_nov_daily_to_display = df_keluar_masuk_nov_daily_to_display.rename(columns = {
            'count' : 'Jumlah'
        })
        
        if df_keluar_masuk_nov_daily_to_display['Jumlah'].sum() > 0:
            fig = px.bar(
                df_keluar_masuk_nov_daily_to_display,
                x = 'Status',
                y = 'Jumlah',
                title = 'Rekapitulasi Keluar/Masuk Tanggal {}'.format(pd.to_datetime(tgl_input).strftime('%d %B %Y').lstrip('0')),
                template = 'none',
                barmode = 'group',
                text_auto = True
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

            expander_keluar_masuk_daily.plotly_chart(fig, use_container_width = True)
        else:
            expander_keluar_masuk_daily.markdown('#### Tidak Ada Aktivitas Keluar/Masuk HP Pada Tanggal {}'.format(pd.to_datetime(tgl_input).strftime('%d %B %Y').lstrip('0')))
    else: 
        expander_keluar_masuk_daily.markdown('#### Silahkan Pilih Tanggal Pada Periode {} {}'.format(calendar.month_name[bulan], tahun))

expander_keluar_masuk_nama = st.expander('Rekapitulasi Keluar/Masuk HP')

li_memori = df_stok.apply(lambda x: expand_cek_stok(x['Nama Barang Clean']), axis = 1)
nama_barang_no_memori = li_memori.str[0]
ram = li_memori.str[1]
rom = li_memori.str[2]
    
df_stok['RAM'] = ram
df_stok['ROM'] = rom

df_stok[['RAM', 'ROM']] = df_stok[['RAM', 'ROM']].astype('int64')

df_stok['Nama Barang no_memori'] = nama_barang_no_memori

df_stok_nama_small = df_stok[[
    'Nama Barang no_memori',
    'RAM',
    'ROM',
    'Nama Barang Clean'
]].drop_duplicates().sort_values(by = ['Nama Barang no_memori', 'RAM', 'ROM'])

options = ['-- Pilih HP --'] + list(df_stok_nama_small['Nama Barang Clean'])
nama_hp = expander_keluar_masuk_nama.selectbox(
    'Pilih Nama HP',
    options = options,
    index = 0
)

if nama_hp != '-- Pilih HP --':
    df_stok_nov_nama = df_stok[
        (df_stok['Nama Barang Clean'] == nama_hp) & 
        (df_stok['bulan_masuk'] == bulan) & 
        (df_stok['tahun_masuk'] == tahun)
    ]

    df_jual_nov_nama = df_stok[
        (df_stok['Nama Barang Clean'] == nama_hp) & 
        (df_stok['bulan_jual'] == bulan) & 
        (df_stok['tahun_jual'] == tahun)
    ]

    df_masuk_nov_g = df_stok_nov_nama\
        .groupby('Tanggal')\
        .agg(count = ('IMEI', 'count'))\
        .reset_index()

    df_jual_nov_g = df_jual_nov_nama\
        .groupby('Tanggal Jual')\
        .agg(count = ('IMEI', 'count'))\
        .reset_index()\
        .rename(columns = {
            'Tanggal Jual' : 'Tanggal'
        })

    df_masuk_nov_g['Status'] = 'Masuk'
    df_jual_nov_g['Status'] = 'Jual'

    df_recap = pd.concat([df_masuk_nov_g, df_jual_nov_g])

    min_date = min(df_stok[
        (df_stok['Tanggal'].dt.year == tahun) & 
        (df_stok['Tanggal'].dt.month == bulan)
    ]['Tanggal'])

    max_date = max(df_stok[
        (df_stok['Tanggal'].dt.year == tahun) & 
        (df_stok['Tanggal'].dt.month == bulan)
    ]['Tanggal'])

    new_idx = pd.DataFrame(data = {
        'Tanggal': pd.date_range(min_date, max_date)
    })

    new_idx['Tanggal'] = pd.to_datetime(new_idx['Tanggal'].dt.strftime('%Y-%m-%d'))

    missing_date = list(new_idx[
        ~new_idx['Tanggal'].isin(df_recap['Tanggal'])
    ]['Tanggal'])

    df_missing_date_masuk = pd.DataFrame(data = {
        'Tanggal' : missing_date,
        'count' : 0,
        'Status' : 'Masuk'
    })

    df_missing_date_jual = pd.DataFrame(data = {
        'Tanggal' : missing_date,
        'count' : 0,
        'Status' : 'Jual'
    })

    df_missing_date = pd.concat([df_missing_date_masuk, df_missing_date_jual])\
        .sort_values(by = 'Tanggal')\
        .reset_index(drop = True)
    
    df_monthly = pd.concat([df_recap, df_missing_date])\
        .reset_index(drop = True)\
        .sort_values(by = ['Tanggal', 'Status'])\
        .set_index(['Tanggal', 'Status'])\
        .unstack()\
        .fillna(0)\
        .astype('int64')\
        .stack()\
        .reset_index()

    df_monthly['Tanggal'] = df_monthly['Tanggal'].astype('datetime64[ns]').dt.strftime('%d-%b').str.lstrip('0')
    df_monthly = df_monthly.rename(columns = {
        'count' : 'Jumlah'
    })

    df_keluar_masuk_nov_nama_to_display = df_monthly.copy()
    df_keluar_masuk_nov_nama_to_display = df_keluar_masuk_nov_nama_to_display.rename(columns = {
        'count' : 'Jumlah'
    })

    if df_keluar_masuk_nov_nama_to_display['Jumlah'].sum() > 0:
        fig = px.line(
            data_frame = df_keluar_masuk_nov_nama_to_display,
            x = 'Tanggal',
            y = 'Jumlah',
            color = 'Status',
            title = 'Rekapitulasi Keluar/Masuk {} {} {}'.format(nama_hp, calendar.month_name[bulan], tahun),
            template = 'none'
        )

        fig.update_layout(
            font_family="Arial",
            font_color="black",
            title_font_family="Arial",
            title_font_color="black",
            legend_title_font_color="black",
            title_font_size = 16,
            title={
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'}
        )

        expander_keluar_masuk_nama.plotly_chart(fig, use_container_width = True)

        tgl_input_nama = expander_keluar_masuk_nama.date_input(
            'Pilih Tanggal',
            key = 'tgl_input_nama',
            value = None
        )

        if tgl_input_nama is not None:
            if tgl_input_nama.month == bulan and tgl_input_nama.year == tahun:
                df_masuk_nov_g = df_stok_nov_nama\
                    .groupby(['Tanggal'])\
                    .agg(count = ('IMEI', 'count'))\
                    .reset_index()

                df_jual_nov_g = df_jual_nov_nama\
                    .groupby(['Tanggal Jual'])\
                    .agg(count = ('IMEI', 'count'))\
                    .reset_index()\
                    .rename(columns = {
                        'Tanggal Jual' : 'Tanggal'
                    })

                df_masuk_nov_g['Status'] = 'Masuk'
                df_jual_nov_g['Status'] = 'Jual'

                df_recap = pd.concat([df_masuk_nov_g, df_jual_nov_g])
            
                min_date = min(df_stok[
                    (df_stok['Tanggal'].dt.year == tahun) & 
                    (df_stok['Tanggal'].dt.month == bulan)
                ]['Tanggal'])

                max_date = max(df_stok[
                    (df_stok['Tanggal'].dt.year == tahun) & 
                    (df_stok['Tanggal'].dt.month == bulan)
                ]['Tanggal'])

                new_idx = pd.DataFrame(data = {
                    'Tanggal': pd.date_range(min_date, max_date)
                })

                new_idx['Tanggal'] = pd.to_datetime(new_idx['Tanggal'].dt.strftime('%Y-%m-%d'))

                missing_date = list(new_idx[
                    ~new_idx['Tanggal'].isin(df_recap['Tanggal'])
                ]['Tanggal'])

                df_missing_date_masuk = pd.DataFrame(data = {
                    'Tanggal' : missing_date,
                    'count' : 0,
                    'Status' : 'Masuk'
                })

                df_missing_date_jual = pd.DataFrame(data = {
                    'Tanggal' : missing_date,
                    'count' : 0,
                    'Status' : 'Jual'
                })
                df_missing_date = pd.concat([df_missing_date_masuk, df_missing_date_jual])\
                    .sort_values(by = 'Tanggal')\
                    .reset_index(drop = True)
                
                df_monthly = pd.concat([df_recap, df_missing_date])\
                    .reset_index(drop = True)\
                    .sort_values(by = ['Tanggal', 'Status'])\
                    .set_index(['Tanggal', 'Status'])\
                    .unstack(level = 1)\
                    .fillna(0)\
                    .astype('int64')\
                    .stack()\
                    .reset_index()

                df_monthly['Tanggal'] = df_monthly['Tanggal'].astype('datetime64[ns]').dt.strftime('%d-%b').str.lstrip('0')
                df_monthly = df_monthly.rename(columns = {
                    'count' : 'Jumlah'
                })

                df_keluar_masuk_nov_nama_daily_to_display = df_monthly.copy()
                df_keluar_masuk_nov_nama_daily_to_display = df_keluar_masuk_nov_nama_daily_to_display[
                    df_keluar_masuk_nov_nama_daily_to_display['Tanggal'] == tgl_input_nama.strftime('%d-%b').lstrip('0')
                ].rename(columns = {
                    'count' : 'Jumlah'
                })

                if df_keluar_masuk_nov_nama_daily_to_display['Jumlah'].sum() > 0:
                    fig = px.bar(
                        df_keluar_masuk_nov_nama_daily_to_display,
                        x = 'Status',
                        y = 'Jumlah',
                        title = 'Rekapitulasi Keluar/Masuk {} Tanggal {}\n'.format(nama_hp, pd.to_datetime(tgl_input_nama).strftime('%d %B %Y').lstrip('0')),
                        template = 'none',
                        barmode = 'group',
                        text_auto = True
                    )

                    fig.update_layout(
                        font_family="Arial",
                        font_color="black",
                        title_font_family="Arial",
                        title_font_color="black",
                        legend_title_font_color="black",
                        title_font_size = 16,
                        title={
                            'y':0.9,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'}
                    )

                    fig.update_traces(textfont_size=20, textangle=0, textposition="outside", cliponaxis=False)

                    expander_keluar_masuk_nama.plotly_chart(fig, use_container_width = True)
                else:
                    expander_keluar_masuk_nama.markdown('#### Tidak ada Keluar/Masuk HP {} Pada Tanggal {}'.format(nama_hp, pd.to_datetime(tgl_input_nama).strftime('%d %B %Y').lstrip('0')))
            else:
                expander_keluar_masuk_nama.markdown('#### Silahkan Pilih Tanggal Pada Periode {} {}'.format(calendar.month_name[bulan], tahun))
    else:
        expander_keluar_masuk_nama.markdown('#### Tidak ada Keluar/Masuk HP {} Pada Bulan {} {}'.format(nama_hp, calendar.month_name[bulan], tahun))                    
