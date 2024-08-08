import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import calendar
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
  
def formatrupiah(uang):
    y = str(uang)
    if len(y) <= 3:
        return ('Rp. ' + y)
    else :
        p = y[-3:]
        q = y[:-3]
        return (formatrupiah(q) + '.' + p)

def clean_data(nama_barang, brand):
    nama_barang_clean = nama_barang.strip()
    li_nama_barang = nama_barang_clean.split(' ')

    if brand == 'Iphone':
        nama_barang = ' '.join(li_nama_barang[0:-2])
        memori      = ' '.join(li_nama_barang[-2:0])
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
            ram         = li_memori[0]
            rom         = li_memori[1]
        else:
            nama_barang = ' '.join(li_nama_barang)
            memori      = '' 
            ram = rom   = 0

    return [nama_barang_clean, memori, ram, rom, nama_barang]

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

    df['Nomor Bon'] = df['Nomor Bon'].fillna('0')
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
df_stok['Nama Barang Clean'] = [nama_barang_brand.replace(brand, '').strip() for (nama_barang_brand, brand) in zip(df_stok['Nama Barang Brand'], df_stok['Brand'])]

_, ctr, _ = st.columns([4,8,3])
with ctr:
    st.markdown('# STOK OK')

total_barang = df_stok[
    df_stok['Status'] == 'Belum Terjual'
].shape[0]

df_stok_not_masuk = df_stok[
    df_stok['Status'] == 'Belum Terjual'
]

expander_jumlah_barang = st.expander("Jumlah Barang", expanded = True)
_, ctr, _ = st.columns([2,6,2])
with ctr:
    expander_jumlah_barang.write('# Jumlah Barang: {} Unit'.format(total_barang))


expander_jumlah_hp = st.expander('Jumlah HP')
df_stok_not_sold = df_stok[
    df_stok['Status'] == 'Belum Terjual'
]

df_stok_not_sold['Brand'] = df_stok_not_sold['Nama Barang'].str.split(' ').str[0].str.strip()
df_stok_not_sold_brand = df_stok_not_sold.groupby('Brand').agg(Jumlah = ('IMEI', 'count')).reset_index()

fig = px.bar(
    df_stok_not_sold_brand,
    x = 'Brand',
    y = 'Jumlah',
    title = 'Persebaran HP Berdasarkan Brand',
    template = 'none', 
    color_discrete_sequence = ['#009100']*15,
    text_auto=True
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
        'yanchor': 'top'},
    yaxis = dict(
        tickfont = dict(
            size=14
        ),
        title_font=dict(
            size=14
        )
    ),
    xaxis = dict(
        tickfont = dict(
            size=16
        ),
        title_font=dict(
            size=18
        )
    )
)

fig.update_traces(textfont_size=20, textangle=0, textposition="outside", cliponaxis=False)

expander_jumlah_hp.plotly_chart(fig, use_container_width = True)

options = ['-- Pilih Brand HP --'] + list(np.sort(df_stok['Brand'].unique()))
nama_to_find = expander_jumlah_hp.selectbox(
    'Pilih Brand HP',
    options = options,
    index = 0
)

if nama_to_find != '-- Pilih Brand HP --':
    df_stok_nama = df_stok_not_masuk[
        df_stok_not_masuk['Nama Barang'].str.startswith(nama_to_find)
    ]
    if df_stok_nama.shape[0] > 0:
        df_stok_nama['Status'] = ['Belum Terjual' if df_stok_nama.loc[x, 'Status'] == 'Belum Terjual' else 'Terjual' for x in df_stok_nama.index]
        
        df_stok_brand = df_stok_nama[
            df_stok_nama['Brand'] == nama_to_find
        ][[
            'Nama Barang',
            'Brand',
            'Status',
            'IMEI'
        ]]

        qty_brand = df_stok_brand.shape[0]

        if qty_brand == 0:
            str_brand = '### Terdapat :red[{}] Unit HP :red[{}]'.format(qty_brand, nama_to_find)
        else:
            str_brand = '### Terdapat :violet[{}] Unit HP :violet[{}]'.format(qty_brand, nama_to_find)

        expander_jumlah_hp.write(str_brand)

        if qty_brand > 0:                    
            li_nama_memori = df_stok_brand.apply(lambda x: clean_data(x['Nama Barang'], x['Brand']), axis=1)
            
            df_stok_brand['Nama Barang Clean']     = li_nama_memori.str[0]
            df_stok_brand['Nama Barang no_memori'] = li_nama_memori.str[4]
            df_stok_brand['Memori']                = li_nama_memori.str[1]
            df_stok_brand['RAM']                   = li_nama_memori.str[2]
            df_stok_brand['ROM']                   = li_nama_memori.str[3]

            df_stok_brand[['RAM', 'ROM']] = df_stok_brand[['RAM', 'ROM']].astype('int64')

            df_stok_brand = df_stok_brand[
                df_stok_brand['Status'] == 'Belum Terjual'
            ].sort_values(by = ['Nama Barang no_memori', 'RAM', 'ROM'])


            df_stok_brand = df_stok_brand\
                .groupby(['Nama Barang Clean'])\
                .agg(Jumlah = ('IMEI', 'count'))\
                .reset_index()
            
            li_memori = df_stok_brand.apply(lambda x: expand_cek_stok(x['Nama Barang Clean']), axis = 1)
            nama_barang_no_memori = li_memori.str[0]
            ram = li_memori.str[1]
            rom = li_memori.str[2]
                
            df_stok_brand['RAM'] = ram
            df_stok_brand['ROM'] = rom
            df_stok_brand[['RAM', 'ROM']] = df_stok_brand[['RAM', 'ROM']].astype('int64')

            df_stok_brand['Nama Barang no_memori'] = nama_barang_no_memori

            df_stok_brand = df_stok_brand\
                .sort_values(by = ['Nama Barang no_memori', 'RAM', 'ROM'])[[
                    'Nama Barang Clean', 
                    'Nama Barang no_memori',
                    'Jumlah'
                ]]
                
            li_detail = [
                expander_jumlah_hp.write('{}. **:green[{}] ; Terdapat :blue[{} unit]**'.format(idx+1, nama_barang, qty))\
                for idx, (nama_barang, qty) in enumerate(
                    zip(
                        df_stok_brand['Nama Barang Clean'],
                        df_stok_brand['Jumlah']
                    )
                )
            ]
            
    else:
        expander_jumlah_hp.write('### Tidak Ada HP {} yang Tersedia di Toko'.format(nama_to_find))
                            
col_tahun, col_bulan = st.columns(2)

df_stok['Tanggal'] = df_stok['Tanggal'].astype('datetime64[ns]')

df_stok['tahun_masuk'] = df_stok['Tanggal'].dt.year
df_stok['bulan_masuk'] = df_stok['Tanggal'].dt.month

with col_tahun:
    options = list(df_stok['tahun_masuk'].unique())

    tahun = st.selectbox(
        'Tahun',
        options = options
    )
with col_bulan:
    options = np.sort(list(df_stok['bulan_masuk'].unique()))

    bulan = st.selectbox(
        'Bulan',
        options = options
    )

df_jual_november = df_stok[
    (df_stok['tahun_masuk'] == tahun) & 
    (df_stok['bulan_masuk'] == bulan)
]

df_jual_november['User'] = df_jual_november['User'].str.lower().str.title()
df_jual_november['Penjual'] = df_jual_november['Penjual'].str.lower().str.title().str.strip()
df_jual_november = df_jual_november[
    ~df_jual_november['Penjual'].isin(['Brand', ''])
]

df_jual_november_to_display = df_jual_november.groupby(['Penjual']).agg(Jumlah = ('IMEI', 'count')).sort_values(by = 'Jumlah').reset_index()

df_jual_november = df_stok[
    (df_stok['tahun_masuk'] == tahun) & 
    (df_stok['bulan_masuk'] == bulan)
]

if df_jual_november.shape[0] > 0:
    df_jual_november_depo = df_jual_november[
        df_jual_november['Penjual'] == 'Brand'
    ].reset_index(drop = True)

    if df_jual_november_depo.shape[0] > 0:
        df_jual_november_depo['Brand'] = [
            'Xiaomi Poco'\
                if x.startswith('Xiaomi Poco')\
                else x.split(' ')[0]\
            for x in df_jual_november_depo['Nama Barang']
        ]

        df_jual_november_depo_to_display = df_jual_november_depo.groupby(['Brand']).agg(Jumlah = ('IMEI', 'count')).sort_values(by = 'Jumlah').reset_index()
    else:
        df_jual_november_depo_to_display = pd.DataFrame(columns = ['Brand', 'Jumlah'])
else:
    df_jual_november_to_display = pd.DataFrame(columns = ['Brand', 'Jumlah'])


expander_sumber_barang = st.expander('Sumber Barang')

fig = px.bar(
    df_jual_november_to_display.tail(15),
    x = 'Penjual',
    y = 'Jumlah',
    title = 'Rekapitulasi Sumber Barang',
    template = 'none',
    color_discrete_sequence = ['blue']*15,
    text_auto = True
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
        'yanchor': 'top'},
    yaxis = dict(
        tickfont = dict(
            size=14
        ),
        title_font=dict(
            size=14
        )
    ),
    xaxis = dict(
        tickfont = dict(
            size=16
        ),
        title_font=dict(
            size=18
        )
    )
)

fig.update_traces(textfont_size=20, textangle=0, textposition="outside", cliponaxis=False)

expander_sumber_barang.plotly_chart(fig, use_container_width = True)
expander_sumber_barang.markdown('#### Notes: Sumber Barang Terbanyak dari: ')

penjual = df_jual_november_to_display.sort_values(by = 'Jumlah', ascending = False)['Penjual']

for idx, i in enumerate(penjual):
    expander_sumber_barang.write('{}. :green[**{}**]'.format(idx+1, i))

    if idx == 2:
        break

expander_masuk_brand = st.expander('Rekapitulasi Masuk per Brand')

li_brand = np.sort(df_stok['Brand'].unique())

for brand_name in li_brand:
    file_path = 'output/laporan/masuk/{}/{}'.format(tahun, brand_name)

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    df_stok_brand_masuk = df_stok[
        (df_stok['Brand'] == brand_name) & 
        (df_stok['tahun_masuk'] == tahun) & 
        (df_stok['bulan_masuk'] == bulan)
    ]

    df_stok_brand_masuk['IMEI'] = df_stok_brand_masuk['IMEI'].astype('str')

    if brand_name == 'Infinix':
        expander_masuk_brand.markdown('### <span style="color: #69ff09">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Itel':
        expander_masuk_brand.markdown('### <span style="color: #fc093d">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Iphone':
        expander_masuk_brand.markdown('### <span style="color: black">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Nokia':
        expander_masuk_brand.markdown('### <span style="color: #234b9b">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Oppo':
        expander_masuk_brand.markdown('### <span style="color: #046a38">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Realme':
        expander_masuk_brand.markdown('### <span style="color:#ffcb1c">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Samsung':
        expander_masuk_brand.markdown('### <span style="color: #0b54a5">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Tecno':
        expander_masuk_brand.markdown('### <span style="color: #0878cb">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Vivo':
        expander_masuk_brand.markdown('### <span style="color: #4764ff">{}</span>'.format(brand_name), unsafe_allow_html = True)

    elif brand_name == 'Xiaomi':
        expander_masuk_brand.markdown('### <span style="color: #ff6e08">{}</span>'.format(brand_name), unsafe_allow_html = True)

    else:
        expander_masuk_brand.markdown('### {}'.format(brand_name))

    file_path = 'output/laporan/keluar/{}/{}'.format(tahun, brand_name)

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    if df_stok_brand_masuk.shape[0] > 0:
        df_stok_brand_masuk = df_stok_brand_masuk.reset_index(drop = True)
        df_masuk_expand = expand_stok(df_stok_brand_masuk)

        df_masuk_bulan_group = df_masuk_expand\
            .groupby(['Tanggal', 'Nama Barang'])\
            .agg(Total = ('IMEI', 'count'))\
            .reset_index()

        df_masuk_bulan_group = df_masuk_bulan_group[
            df_masuk_bulan_group['Total'] > 0
        ]
        
        li_memori = df_masuk_bulan_group.apply(lambda x: expand_cek_stok(x['Nama Barang']), axis = 1)
        df_masuk_bulan_group['Nama Barang no_memori'] = li_memori.str[0]
        df_masuk_bulan_group['RAM'] = li_memori.str[1].astype('int64')
        df_masuk_bulan_group['ROM'] = li_memori.str[2].astype('int64')
        
        df_masuk_bulan_group = df_masuk_bulan_group\
            .sort_values(by = ['Tanggal', 'Nama Barang no_memori', 'RAM', 'ROM', 'Total'])

        df_masuk_bulan_warna = df_stok_brand_masuk[[
            'Tanggal',
            'Nama Barang',
            'Warna'
        ]]

        df_masuk_bulan_warna_group = df_masuk_bulan_warna\
            .groupby(['Tanggal', 'Nama Barang', 'Warna'])\
            .agg(Jumlah = ('Tanggal', 'count'))

        df_masuk_bulan_warna_group = df_masuk_bulan_warna_group[
            df_masuk_bulan_warna_group['Jumlah'] > 0
        ].reset_index()

        df_masuk_bulan_warna_detail = pd.merge(\
            df_masuk_bulan_group, df_masuk_bulan_warna_group, \
            on = ['Tanggal', 'Nama Barang'], how = 'inner'\
        ).rename(columns = {
            'Jumlah_y' : 'Jumlah'    
        })

        df_masuk_bulan_imei = df_stok_brand_masuk[[
            'Tanggal',
            'Nama Barang',
            'Warna',
            'IMEI',
            'IMEI_last_4',
            'Penjual',
            'Penerima'
        ]]

        df_masuk_bulan_warna_detail_no_idx = df_masuk_bulan_warna_detail.reset_index()
        df_masuk_bulan_tipe_warna_imei_detail = pd.merge(\
            df_masuk_bulan_warna_detail_no_idx, df_masuk_bulan_imei,
            on = ['Tanggal', 'Nama Barang', 'Warna'], how = 'inner'\
        )

        df_masuk_bulan_group = df_masuk_bulan_group.astype('str')
        df_masuk_bulan_warna_detail = df_masuk_bulan_warna_detail.astype('str')
        df_masuk_bulan_tipe_warna_imei_detail = df_masuk_bulan_tipe_warna_imei_detail.astype('str')

        df_masuk_bulan_group_idx = df_masuk_bulan_group[[
            'Tanggal',
            'Nama Barang',
            'Total',
        ]].set_index(['Tanggal', 'Nama Barang'])

        df_masuk_bulan_warna_detail = df_masuk_bulan_warna_detail[[
            'Tanggal',
            'Nama Barang',
            'Total',
            'Warna',
            'Jumlah'
        ]].set_index(['Tanggal', 'Nama Barang', 'Total', 'Warna'])

        df_masuk_bulan_tipe_warna_imei_detail = df_masuk_bulan_tipe_warna_imei_detail[[
            'Tanggal',
            'Nama Barang',
            'Total',
            'Warna',
            'Jumlah',
            'IMEI',
            'IMEI_last_4',
            'Penjual',
            'Penerima'
        ]].set_index(['Tanggal', 'Nama Barang', 'Total', 'Warna', 'Jumlah', 'IMEI'])

        if df_masuk_bulan_group_idx.shape[0] > 0:
            writer = pd.ExcelWriter('output/laporan/masuk/{}/{}/masuk_{}_{}.xlsx'.format(tahun, brand_name, brand_name, calendar.month_name[bulan][:3]), engine = 'xlsxwriter')
            workbook = writer.book

            fmt_number = workbook.add_format({
                'num_format' : '0'
            })

            if df_masuk_bulan_group_idx.shape[0] > 0:
                df_masuk_bulan_group_idx.to_excel(writer, sheet_name = 'Stok')
                df_masuk_bulan_warna_detail.to_excel(writer, sheet_name = 'Stok + Warna')
                df_masuk_bulan_tipe_warna_imei_detail.to_excel(writer, sheet_name = 'Stok + Warna + IMEI')

                worksheet_tipe   = writer.sheets['Stok']
                worksheet_warna  = writer.sheets['Stok + Warna']
                worksheet_imei   = writer.sheets['Stok + Warna + IMEI']

                for i, col_1 in enumerate(df_masuk_bulan_group_idx.reset_index().columns):
                    width_1 = max(df_masuk_bulan_group_idx.reset_index()[col_1].apply(lambda x: len(str(x))).max(), len(col_1))
                    worksheet_tipe.set_column(i,i, width_1)

                for j, col_2 in enumerate(df_masuk_bulan_warna_detail.reset_index().columns):
                    width_2 = max(df_masuk_bulan_warna_detail.reset_index()[col_2].apply(lambda x: len(str(x))).max(), len(col_2))
                    worksheet_warna.set_column(j,j, width_2)

                for k, col_3 in enumerate(df_masuk_bulan_tipe_warna_imei_detail.reset_index().columns):
                    width_3 = max(df_masuk_bulan_tipe_warna_imei_detail.reset_index()[col_3].apply(lambda x: len(str(x))).max(), len(col_3))
                    worksheet_imei.set_column(k,k, width_3)

            workbook.close()

            with open('output/laporan/masuk/{}/{}/masuk_{}_{}.xlsx'.format(tahun, brand_name, brand_name, calendar.month_name[bulan][:3]), 'rb') as my_file:
                expander_masuk_brand.download_button(
                    label = 'Download Laporan HP {} Masuk Bulan {} {}'.format(brand_name, calendar.month_name[bulan], tahun), 
                    data = my_file, 
                    file_name = '{}_Masuk_{}.xlsx'.format(brand_name, calendar.month_name[bulan][:3] + str(tahun)[-2:]), 
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    else:
        expander_masuk_brand.write('Tidak Ada Masuk {}'.format(brand_name))
