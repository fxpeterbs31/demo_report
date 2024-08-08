import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import calendar
import os
import locale
locale.setlocale(locale.LC_ALL, 'id_ID')

st.set_page_config(page_title = 'Demo Laporan OK')

st.session_state.stats_income_general   = False
st.session_state.plot_income_general    = False
st.session_state.stats_income           = False

st.session_state.show_profit_stats      = False
st.session_state.show_profit_plot       = False

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

def expand_stok(df):        
    df['Tanggal']        = df['Tanggal'].astype('datetime64[ns]')
    df['Tanggal Jual']   = df['Tanggal Jual'].astype('datetime64[ns]')

    df['IMEI'] = df['IMEI'].astype('str')
    df['IMEI_last_4']   = df['IMEI'].str[-4:]

    df['Harga Jual'] = ['0' if x == '' else x for x in df['Harga Jual']]
    df['Harga Jual'] = df['Harga Jual'].astype('int64')

    df['Nomor Bon'] = ['0' if x == '' else x for x in df['Nomor Bon']]
    df['Nomor Bon'] = df['Nomor Bon'].astype('int64')

    df['Harga'] = df['Harga'].str.replace('Rp. ', '').str.replace('.', '').str.replace(',-', '')

    df['Harga'] = ['0' if x == '' else x for x in df['Harga']]
    df['Harga'] = df['Harga'].astype('int64')

    nama_barang = df['Nama Barang'].str.split('(').str[0].str.strip()
    df['Nama Barang'] = nama_barang
    
    df[['Warna', 'Status']] = df[['Warna', 'Status']].astype('category')

    params = [
        'Tanggal',
        'Nama Barang',
        'Warna',
        'Harga',
        'IMEI',
        'IMEI_last_4',
        'Status',
        'Tanggal Jual',
        'Harga Jual',
        'Nomor Bon',
        'Penjual',
        'Penerima',
        'User'
    ]
    df = df[params]
    
    return df

df_stok = pd.read_excel('demo_data.xlsx')
df_stok['Brand'] = [x.split(' ')[0].strip() for x in df_stok['Nama Barang']]
df_stok['Nama Barang Brand'] = [x.split('(')[0].strip() for x in df_stok['Nama Barang']]
df_stok['Nama Barang Clean'] = [nama_barang_brand.replace(brand, '').strip for (nama_barang_brand, brand) in zip(df_stok['Nama Barang Brand'], df_stok['Brand'])]

df_stok['Tanggal Jual'] = pd.to_datetime(df_stok['Tanggal Jual'], errors = 'coerce')

df_stok['tahun_jual'] = df_stok['Tanggal Jual'].dt.year
df_stok['bulan_jual'] = df_stok['Tanggal Jual'].dt.month

_, ctr, _ = st.columns([2.5,8,1.5])
with ctr:
    st.markdown('# PENJUALAN OK')

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

expander_penjualan = st.expander('Penjualan Umum', expanded = True)

df_sold_november = df_stok[
    (df_stok['tahun_jual'] == tahun) & 
    (df_stok['bulan_jual'] == bulan)
]

expander_penjualan.markdown('#### Jumlah HP yang terjual bulan {} {} : <span style="color: #808000;">{}</span> unit'.format(calendar.month_name[bulan], tahun, df_sold_november.shape[0]), unsafe_allow_html = True)

if 'general_info_penjualan' not in st.session_state:
    st.session_state.general_info_penjualan = False

def callback_general_info_penjualan():
    st.session_state.general_info_penjualan = True

df_sold_november_g = df_sold_november.groupby('Tanggal Jual').agg(count = ('IMEI', 'count'))
btn_general_info_penjualan = expander_penjualan.button('Lihat Detail Penjualan', on_click = callback_general_info_penjualan)

if btn_general_info_penjualan or st.session_state.general_info_penjualan:
    df_sold_november_stats = df_sold_november_g.describe()

    mean = df_sold_november_stats.loc['mean', 'count']
    median = df_sold_november_stats.loc['50%', 'count']
    min_sales = df_sold_november_stats.loc['min', 'count']
    max_sales = df_sold_november_stats.loc['max', 'count']

    min_sales_date = pd.to_datetime(str(df_sold_november_g[
        df_sold_november_g['count'] == min_sales
    ].index.values[0])).strftime('%d %B %Y')

    max_sales_date = pd.to_datetime(str(df_sold_november_g[
        df_sold_november_g['count'] == max_sales
    ].index.values[0])).strftime('%d %B %Y')

    expander_penjualan.markdown('##### Rata-rata penjualan : <span style="color: #808000;">{}</span> unit'.format(int(mean)), unsafe_allow_html = True)
    expander_penjualan.markdown('##### Median penjualan    : <span style="color: #808000;">{}</span> unit'.format(int(median)), unsafe_allow_html = True)
    expander_penjualan.markdown('##### Penjualan terendah  : <span style="color: #808000;">{}</span> unit ; Tanggal <span style="color: #808000;">{}</span>'.format(int(min_sales), min_sales_date.lstrip('0')), unsafe_allow_html = True)
    expander_penjualan.markdown('##### Penjualan tertinggi : <span style="color: #808000;">{}</span> unit ; Tanggal <span style="color: #808000;">{}</span>'.format(int(max_sales), max_sales_date.lstrip('0')), unsafe_allow_html = True)

    if 'grafik_penjualan' not in st.session_state:
        st.session_state.grafik_penjualan = False

    def callback_grafik_penjualan():
        st.session_state.grafik_penjualan = True        

    btn_grafik_penjualan = expander_penjualan.button('Lihat Grafik Penjualan', on_click = callback_grafik_penjualan)

    if btn_grafik_penjualan or st.session_state.grafik_penjualan:
        df_sold_november_g_to_display = df_sold_november_g.reset_index()
        df_sold_november_g_to_display['Tanggal Jual'] = pd.to_datetime(df_sold_november_g_to_display['Tanggal Jual']).dt.strftime('%d-%b').str.lstrip('0')

        df_sold_november_g_to_display = df_sold_november_g_to_display.rename(columns = {
            'count' : 'Jumlah'
        })

        fig = px.line(
            data_frame = df_sold_november_g_to_display,
            x = 'Tanggal Jual',
            y = 'Jumlah',
            title = 'Penjualan Bulan {} {}\n'.format(calendar.month_name[bulan], tahun),
            template = 'none',
            color_discrete_sequence = ['#808000']
        )

        fig.update_layout(
            font_family="Arial",
            font_color="black",
            title_font_family="Arial",
            title_font_color="black",
            legend_title_font_color="black",
            title_font_size = 35,
            title={
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'}
        )

        expander_penjualan.plotly_chart(fig, use_container_width = True)

expander_brand_sold_recap = st.expander('Penjualan per Brand', expanded = True)
df_stok_sold = df_stok[
    (df_stok['Status'] == 'Terjual') & 
    (df_stok['tahun_jual'] == tahun) & 
    (df_stok['bulan_jual'] == bulan)
]

df_stok_sold_brand = df_stok_sold.groupby('Brand').agg(Jumlah = ('IMEI', 'count')).reset_index()
fig = px.bar(
    data_frame = df_stok_sold_brand,
    x = 'Brand',
    y = 'Jumlah',
    title = 'Penjualan per Brand Bulan {} {}\n'.format(calendar.month_name[bulan], tahun),
    template = 'none',
    color_discrete_sequence = ['#009100']
)

fig.update_layout(
    font_family="Arial",
    font_color="black",
    title_font_family="Arial",
    title_font_color="black",
    legend_title_font_color="black",
    title_font_size = 35,
    title={
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)

expander_brand_sold_recap.plotly_chart(fig, use_container_width = True)


expander_penjualan = st.expander('Penjualan Barang', expanded = True)
df_sold_november = df_stok[
    (df_stok['tahun_jual'] == tahun) & 
    (df_stok['bulan_jual'] == bulan)
]

df_sold_november['Brand'] = df_sold_november['Nama Barang'].str.split(' ').str[0]
df_sold_november_g = df_sold_november.groupby('Brand').agg(Jumlah = ('IMEI', 'count')).sort_values(by = 'Jumlah').reset_index()

expander_penjualan.markdown('##### Total : :red[{}] unit'.format(df_sold_november.shape[0]))

if 'stats_penjualan' not in st.session_state:
    st.session_state.stats_penjualan = False

def callback_penjualan():
    st.session_state.stats_penjualan = True

btn_stats_penjualan = expander_penjualan.button('Lihat Detail Penjualan Barang', on_click = callback_penjualan)
if btn_stats_penjualan or st.session_state.stats_penjualan:
    fig = px.bar(
        df_sold_november_g,
        x = 'Brand',
        y = 'Jumlah',
        title = 'Penjualan Barang Bulan {} {}'.format(calendar.month_name[bulan], tahun),
        template = 'none',
        color_discrete_sequence = ['red']*15,
        text_auto = True
    )

    fig.update_layout(
        font_family="Arial",
        font_color="black",
        title_font_family="Arial",
        title_font_color="black",
        legend_title_font_color="black",
        title_font_size = 15,
        title={
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )

    fig.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False)

    expander_penjualan.plotly_chart(fig, use_container_width = True)

expander_brand = st.expander('Laporan Penjualan per Brand')

li_brand = np.sort(df_stok['Brand'].unique())

for brand_name in li_brand:
    df_stok_brand_sold = df_stok[
        (df_stok['Status'] == 'Terjual') & 
        (df_stok['Brand'] == brand_name) & 
        (df_stok['tahun_jual'] == tahun) & 
        (df_stok['bulan_jual'] == bulan)
    ]

    df_stok_brand_sold['IMEI'] = df_stok_brand_sold['IMEI'].astype('str')


    if brand_name == 'Infinix':
        expander_brand.markdown('### <span style="color: #69ff09">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Itel':
        expander_brand.markdown('### <span style="color: #fc093d">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Iphone':
        expander_brand.markdown('### <span style="color: black">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Nokia':
        expander_brand.markdown('### <span style="color: #234b9b">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Oppo':
        expander_brand.markdown('### <span style="color: #046a38">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Realme':
        expander_brand.markdown('### <span style="color:#ffcb1c">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Samsung':
        expander_brand.markdown('### <span style="color: #0b54a5">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Tecno':
        expander_brand.markdown('### <span style="color: #0878cb">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Vivo':
        expander_brand.markdown('### <span style="color: #4764ff">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Xiaomi':
        expander_brand.markdown('### <span style="color: #ff6e08">{}</span>'.format(brand_name), unsafe_allow_html = True)

    else:
        expander_brand.markdown('### {}'.format(brand_name))

    file_path = 'output/laporan/keluar/{}/{}'.format(tahun, brand_name)

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    # depo
    # df_stok_brand_sold = df_stok_brand_sold[
    #     df_stok_brand_sold['Tipe'] == 'Depo'
    # ]

    if df_stok_brand_sold.shape[0] > 0:
        df_stok_brand_sold = df_stok_brand_sold.reset_index(drop = True)
        df_stok_brand_sold_expand = expand_stok(df_stok_brand_sold)

        params = [
            'Nomor Bon',
            'Tanggal Jual',
            'Nama Barang',
            'Warna',
            'IMEI',
            'Harga',
            'Harga Jual',
            'User'
        ]

        df_stok_brand_sold[['Nomor Bon', 'IMEI']] = df_stok_brand_sold[['Nomor Bon', 'IMEI']].astype('str')
        df_stok_brand_sold['Tanggal Jual'] = df_stok_brand_sold['Tanggal Jual'].astype('datetime64[ns]').dt.strftime('%d-%b-%Y')
        df_stok_brand_sold['Harga Jual'] = df_stok_brand_sold['Harga Jual'].astype('int64')
        df_stok_brand_sold = df_stok_brand_sold.sort_values(by = 'Nomor Bon')

        buku_penjualan_brand = df_stok_brand_sold[params]

        buku_penjualan_brand['Profit'] = [
            formatrupiah(jual-modal) \
                if modal not in [0, 1000] \
                else '' \
            for jual, modal in zip(
                buku_penjualan_brand['Harga Jual'], 
                buku_penjualan_brand['Harga']
            )
        ]

        buku_penjualan_brand['Harga'] = buku_penjualan_brand['Harga'].apply(formatrupiah)
        buku_penjualan_brand['Harga Jual'] = buku_penjualan_brand['Harga Jual'].apply(formatrupiah)

        buku_penjualan_brand = buku_penjualan_brand.astype('str').set_index(['Nomor Bon'])

        df_keluar_bulan_group = df_stok_brand_sold\
            .groupby(['Tanggal Jual', 'Nama Barang'])\
            .agg(Total = ('IMEI', 'count'))\
            .reset_index()

        df_keluar_bulan_detail = df_keluar_bulan_group[
            df_keluar_bulan_group['Total'] > 0
        ]

        # urutin memori
        li_memori = df_keluar_bulan_detail.apply(lambda x: expand_cek_stok(x['Nama Barang']), axis = 1)
        nama_barang_no_memori = li_memori.str[0]
        ram = li_memori.str[1]
        rom = li_memori.str[2]
            
        df_keluar_bulan_detail['RAM'] = ram
        df_keluar_bulan_detail['ROM'] = rom
        
        df_keluar_bulan_detail[['RAM', 'ROM']] = df_keluar_bulan_detail[['RAM', 'ROM']].astype('int64')

        df_keluar_bulan_detail['Nama Barang no_memori'] = nama_barang_no_memori

        df_keluar_bulan_detail = df_keluar_bulan_detail\
            .sort_values(by = ['Tanggal Jual', 'Nama Barang no_memori', 'RAM', 'ROM'])

        df_keluar_bulan_warna = df_stok_brand_sold[[
            'Tanggal Jual',
            'Nama Barang',
            'Warna'
        ]]

        df_keluar_bulan_warna_group = df_keluar_bulan_warna\
            .groupby(['Tanggal Jual', 'Nama Barang', 'Warna'])\
            .agg(Jumlah = ('Tanggal Jual', 'count'))

        df_keluar_bulan_warna_group = df_keluar_bulan_warna_group[
            df_keluar_bulan_warna_group['Jumlah'] > 0
        ].reset_index()

        df_keluar_bulan_warna_detail = pd.merge(\
            df_keluar_bulan_detail, df_keluar_bulan_warna_group, \
            on = ['Tanggal Jual', 'Nama Barang'], \
            how = 'inner'\
        ).rename(columns = {
            'Jumlah_x' : 'Sub Total', 
            'Jumlah_y' : 'Jumlah'    
        })

        df_keluar_bulan_imei = df_stok_brand_sold[[
            'Tanggal Jual',
            'Nama Barang',
            'Warna',
            'IMEI',
            'IMEI_last_4',
            'User',
            'Penjual',
            'Penerima',
            'Harga',
            'Harga Jual'
        ]]

        df_keluar_bulan_warna_detail_no_idx = df_keluar_bulan_warna_detail.reset_index()
        df_keluar_bulan_tipe_warna_imei_detail = pd.merge(\
            df_keluar_bulan_warna_detail_no_idx, df_keluar_bulan_imei,
            on = ['Tanggal Jual', 'Nama Barang', 'Warna'],\
            how = 'inner'\
        )

        df_keluar_bulan_tipe_warna_imei_detail['Harga'] = \
            df_keluar_bulan_tipe_warna_imei_detail['Harga'].apply(formatrupiah)
        
        df_keluar_bulan_tipe_warna_imei_detail['Harga Jual'] = \
            df_keluar_bulan_tipe_warna_imei_detail['Harga Jual'].apply(formatrupiah)

        df_keluar_bulan_detail = df_keluar_bulan_detail.astype('str')
        df_keluar_bulan_warna_detail = df_keluar_bulan_warna_detail.astype('str')
        df_keluar_bulan_tipe_warna_imei_detail = df_keluar_bulan_tipe_warna_imei_detail.astype('str')

        df_keluar_bulan_detail_idx = df_keluar_bulan_detail[[
            'Tanggal Jual',
            'Nama Barang',
            'Total'
        ]].set_index(['Tanggal Jual', 'Nama Barang'])

        df_keluar_bulan_warna_detail = df_keluar_bulan_warna_detail[[
            'Tanggal Jual',
            'Nama Barang',
            'Total',
            'Warna',
            'Jumlah'
        ]].set_index(['Tanggal Jual', 'Nama Barang', 'Total', 'Warna'])

        df_keluar_bulan_tipe_warna_imei_detail = df_keluar_bulan_tipe_warna_imei_detail[[
            'Tanggal Jual',
            'Nama Barang',
            'Total',
            'Warna',
            'Jumlah',
            'IMEI',
            'IMEI_last_4',
            'Penjual',
            'Penerima',
            'User',
            'Harga',
            'Harga Jual'
        ]].set_index(['Tanggal Jual', 'Nama Barang', 'Total', 'Warna', 'Jumlah', 'IMEI'])                

        if df_keluar_bulan_detail_idx.shape[0] > 0:
            writer = pd.ExcelWriter('output/laporan/keluar/{}/{}/jual_{}_{}.xlsx'.format(tahun, brand_name, brand_name, calendar.month_name[bulan][:3]), engine = 'xlsxwriter')
            workbook = writer.book

            fmt_number = workbook.add_format({
                'num_format' : '0'
            })

            if df_keluar_bulan_detail_idx.shape[0] > 0:
                buku_penjualan_brand.to_excel(writer, sheet_name = 'Buku Penjualan')
                df_keluar_bulan_detail_idx.to_excel(writer, sheet_name = 'Stok')
                df_keluar_bulan_warna_detail.to_excel(writer, sheet_name = 'Stok + Warna')
                df_keluar_bulan_tipe_warna_imei_detail.to_excel(writer, sheet_name = 'Stok + Warna + IMEI')

                worksheet_buku_penjualan = writer.sheets['Buku Penjualan']
                worksheet_tipe           = writer.sheets['Stok']
                worksheet_warna          = writer.sheets['Stok + Warna']
                worksheet_imei           = writer.sheets['Stok + Warna + IMEI']

                for l, col_4 in enumerate(buku_penjualan_brand.reset_index().columns):
                    width_4 = max(buku_penjualan_brand.reset_index()[col_4].apply(lambda x: len(str(x))).max(), len(col_4))
                    worksheet_buku_penjualan.set_column(l,l, width_4)

                for i, col_1 in enumerate(df_keluar_bulan_detail_idx.reset_index().columns):
                    width_1 = max(df_keluar_bulan_detail_idx.reset_index()[col_1].apply(lambda x: len(str(x))).max(), len(col_1))
                    worksheet_tipe.set_column(i,i, width_1)

                for j, col_2 in enumerate(df_keluar_bulan_warna_detail.reset_index().columns):
                    width_2 = max(df_keluar_bulan_warna_detail.reset_index()[col_2].apply(lambda x: len(str(x))).max(), len(col_2))
                    worksheet_warna.set_column(j,j, width_2)

                for k, col_3 in enumerate(df_keluar_bulan_tipe_warna_imei_detail.reset_index().columns):
                    width_3 = max(df_keluar_bulan_tipe_warna_imei_detail.reset_index()[col_3].apply(lambda x: len(str(x))).max(), len(col_3))
                    worksheet_imei.set_column(k,k, width_3)

            workbook.close()

            with open('output/laporan/keluar/{}/{}/jual_{}_{}.xlsx'.format(tahun, brand_name, brand_name, calendar.month_name[bulan][:3]), 'rb') as my_file:
                expander_brand.download_button(
                    label = 'Download Laporan HP {} Keluar Bulan {} {}'.format(brand_name, calendar.month_name[bulan], tahun), 
                    data = my_file, 
                    file_name = '{}_Jual_{}.xlsx'.format(brand_name, calendar.month_name[bulan][:3] + str(tahun)[-2:]), 
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    else:
        expander_brand.write('Tidak Ada Penjualan {}'.format(brand_name))

expander_penjualan_nota = st.expander('Nota yang Digunakan', expanded = True)

df_sold_november = df_stok[
    (df_stok['tahun_jual'] == tahun) & 
    (df_stok['bulan_jual'] == bulan)
]

df_sold_november[['Nomor Bon', 'Harga Jual']] = df_sold_november[['Nomor Bon', 'Harga Jual']].astype('int64')

df_sold_november_no_bon_g = df_sold_november.groupby(['Tanggal Jual']).agg(count_bon = ('Nomor Bon', 'nunique'))
df_sold_november_no_bon_stats = df_sold_november_no_bon_g.describe()

count = df_sold_november_no_bon_stats.loc['count', 'count_bon']
mean = df_sold_november_no_bon_stats.loc['mean', 'count_bon']
median = df_sold_november_no_bon_stats.loc['50%', 'count_bon']
min_no_bon = df_sold_november_no_bon_stats.loc['min', 'count_bon']
max_no_bon = df_sold_november_no_bon_stats.loc['max', 'count_bon']

min_no_bon_date = pd.to_datetime(str(df_sold_november_no_bon_g[
    df_sold_november_no_bon_g['count_bon'] == min_no_bon
].index.values[0])).strftime('%d %B %Y')

max_no_bon_date = pd.to_datetime(str(df_sold_november_no_bon_g[
    df_sold_november_no_bon_g['count_bon'] == max_no_bon
].index.values[0])).strftime('%d %B %Y')

expander_penjualan_nota.markdown('### Jumlah bon yang terpakai {} {}: <span style = "color:#FF00FF;">{}</span> bon'.format(calendar.month_name[bulan], tahun, int(df_sold_november_no_bon_g['count_bon'].sum())), unsafe_allow_html = True)

if 'stats_penjualan_nota' not in st.session_state:
    st.session_state.stats_penjualan_nota = False

def callback_penjualan_nota():
    st.session_state.stats_penjualan_nota = True

btn_detail_nota = expander_penjualan_nota.button('Lihat Detail Nota', on_click = callback_penjualan_nota)
if btn_detail_nota or st.session_state.stats_penjualan_nota:
    expander_penjualan_nota.markdown('##### Rata-rata    : <span style = "color:#FF00FF;">{}</span> bon'.format(int(mean)), unsafe_allow_html = True)
    expander_penjualan_nota.markdown('##### Median       : <span style = "color:#FF00FF;">{}</span> bon'.format(int(median)), unsafe_allow_html = True)
    expander_penjualan_nota.markdown('##### Jumlah penggunaan bon terendah   : <span style = "color:#FF00FF;">{}</span> bon ; Pada Tanggal <span style = "color:#FF00FF;">{}</span>'.format(int(min_no_bon), min_no_bon_date), unsafe_allow_html = True)
    expander_penjualan_nota.markdown('##### Jumlah penggunaan bon tertinggi  : <span style = "color:#FF00FF;">{}</span> bon ; Pada Tanggal <span style = "color:#FF00FF;">{}</span>'.format(int(max_no_bon), max_no_bon_date), unsafe_allow_html = True)

    if 'persebaran_nota' not in st.session_state:
        st.session_state.persebaran_nota = False

    def callback_persebaran_nota():
        st.session_state.persebaran_nota = True

    btn_grafik_nota = expander_penjualan_nota.button('Lihat Persebaran Nota', on_click = callback_persebaran_nota)

    if btn_grafik_nota or st.session_state.persebaran_nota:
        df_sold_november_no_bon_g_to_display = df_sold_november_no_bon_g.reset_index()

        df_sold_november_no_bon_g_to_display = df_sold_november_no_bon_g_to_display.rename(columns = {
            'count_bon' : 'Jumlah'
        })

        df_sold_november_no_bon_g_to_display['Tanggal Jual'] = df_sold_november_no_bon_g_to_display['Tanggal Jual'].astype('datetime64[ns]')
        df_sold_november_no_bon_g_to_display['Tanggal Jual'] = df_sold_november_no_bon_g_to_display['Tanggal Jual'].dt.strftime('%d-%b').str.lstrip('0')

        fig = px.line(
            data_frame = df_sold_november_no_bon_g_to_display,
            x = 'Tanggal Jual',
            y = 'Jumlah',
            title = 'Penggunaan Nomor Bon Bulan {} {}\n'.format(calendar.month_name[bulan], tahun),
            template = 'none',
            color_discrete_sequence = ['#FF00FF']
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

        expander_penjualan_nota.plotly_chart(fig, use_container_width = True)

expander_penjualan_qty_vs_nota = st.expander('Perbandingan Penjualan Unit dan Jumlah Nota')

df_sold_november_no_bon_g['Status'] = 'Nota'

df_sold_november_g = df_sold_november.groupby('Tanggal Jual').agg(count = ('IMEI', 'count'))
df_sold_november_g['Status'] = 'Unit'

df_sold_november_no_bon_g = df_sold_november_no_bon_g.rename(columns = {
    'count_bon': 'Jumlah'
})

df_sold_november_g = df_sold_november_g.rename(columns = {
    'count': 'Jumlah'
})

df_sold_november_unit_no_bon = pd.concat([df_sold_november_no_bon_g, df_sold_november_g]).sort_values(by = ['Tanggal Jual', 'Status']).reset_index()

df_sold_november_unit_no_bon_to_display = df_sold_november_unit_no_bon.copy()
df_sold_november_unit_no_bon_to_display['Tanggal Jual'] = df_sold_november_unit_no_bon_to_display['Tanggal Jual'].astype('datetime64[ns]')
df_sold_november_unit_no_bon_to_display['Tanggal Jual'] = df_sold_november_unit_no_bon_to_display['Tanggal Jual'].dt.strftime('%d-%b').str.lstrip('0')

fig = px.line(
    data_frame = df_sold_november_unit_no_bon_to_display,
    x = 'Tanggal Jual',
    y = 'Jumlah',
    color = 'Status',
    title = 'Perbandingan Nota dan Unit Terjual {} {}'.format(calendar.month_name[bulan], tahun),
    template = 'none',
    color_discrete_map = {
        'Nota' : '#FF00FF',
        'Unit' : '#808000'
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

expander_penjualan_qty_vs_nota.plotly_chart(fig, use_container_width = True)
