import streamlit as st

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

_, ctr, _ = st.columns([3,5,3])
with ctr:
    st.markdown(f'# Welcome!')

_, ctr, _ = st.columns([0.5,9,0.5])
with ctr:
    st.markdown('### Silahkan Pilih Menu sesuai dengan keinginan Anda!')
