import streamlit as st
import pandas as pd
import streamlit.components.v1 as components



# Streamlit arayüzünü oluşturma
st.markdown(
    """
    <style>
    .stApp {
        background-color: orange;  /* Arka plan rengi */
    }
    .custom-text {
        font-size: 24px; /* Yazı boyutu */
        color: red;      /* Yazı rengi */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.image("Amazon.png", width=300)
#st.image("Amazon.png", use_column_width=True)

# Veri setlerini yükle
df = pd.read_csv('sepet_analizi.csv')  # Ana veri seti
df['Profit_rate'] = df['Unnamed: 17']
df.drop("Unnamed: 17", axis=1, inplace=True)
df2 = pd.read_csv('for_further_analysis.csv')  # İkinci veri seti


def beraber_satinalma_analizi():
    st.title('Birlikte Satın Alınan Ürün Analizi')
    user_input_asin = st.text_input("Bir ASIN girin:")
    # Kenar çubuğu için ASIN seçici ekle
    unique_asins = df['asin'].unique()  # Veri setinden benzersiz ASIN'leri al
    selected_asin = st.sidebar.selectbox("ASIN Seçiniz", unique_asins)
     # Seçilen ASIN'i bir metin olarak gösterin ve kopyalanabilir yapın
    st.sidebar.text(f"Seçilen ASIN: {selected_asin}")
    

    if user_input_asin:
        # Beraber satın alınan ürünlerin analizini yap
        total_order = df[df.asin == user_input_asin].shape[0]
        filtered_df = df2[df2.eq(user_input_asin).any(axis=1)]
        columns_to_check = ['asin1', 'asin2', 'asin3', 'asin4', 'asin5', 'asin6', 'asin7']
        not_equal_values = []
        

        for column in columns_to_check:
            values = filtered_df[column][filtered_df[column] != user_input_asin]
            value_counts = values.value_counts()
            not_equal_values.extend([(value, count) for value, count in value_counts.items()])

        result_df = pd.DataFrame(not_equal_values, columns=['Value', 'Count'])
        result_df = result_df.groupby('Value')['Count'].sum().reset_index()
        result_df = result_df.sort_values(by='Count', ascending=False)
        result_df['kar_orani'] = df['Profit_rate']*100
        result_df['kar_orani'] = result_df['kar_orani'].round()
        bought_together = result_df['Count'].sum()
        
        st.write('Sipariş Sayısı:', total_order)
        st.write(f'Birlikte Satın Alma Oranı: {bought_together*100/total_order:.2f}%')
        st.write(f'Tek Başına Satın Alma Oranı: {(total_order-bought_together)*100/total_order:.2f}%')
        st.write("Birlikte Satın Alınan Ürünler ve Sayıları:")
        st.dataframe(result_df[['Value', 'Count']])
        st.write("ASIN'ler ve İlgili Kar Yüzdeleri:")
        st.dataframe(result_df[['Value', 'kar_orani']])
        
    
def asin_analizi():
    st.title('ASIN Analizi')

    input_threshold_value = st.number_input("Birlikte satılma yüzdesi için threshold değeri girin:", min_value=0.0, max_value=100.0, value=50.0)
    input_min_ordered = st.number_input("Minimum sipariş sayısı girin:", min_value=1, max_value=10000, value=10)
    
    processed_asins = set()
    columns_to_check = ['asin1', 'asin2', 'asin3', 'asin4', 'asin5', 'asin6', 'asin7']

    if st.button('Analizi Başlat'):
        for col in df2.columns[1:]:
            unique_asins = df2[col].unique()
            for iterated_asin in unique_asins:
                if pd.isnull(iterated_asin) or iterated_asin in processed_asins:
                    continue

                total_order = df[df['asin'] == iterated_asin].shape[0]
                
                if total_order < input_min_ordered:
                    continue

                filtered_df = df2[df2.eq(iterated_asin).any(axis=1)]
                not_equal_values = []

                for column in columns_to_check:
                    values = filtered_df[column][filtered_df[column] != iterated_asin]
                    value_counts = values.value_counts()
                    not_equal_values.extend([(value, count) for value, count in value_counts.items()])

                result_df = pd.DataFrame(not_equal_values, columns=['Value', 'Count'])
                result_df = result_df.groupby('Value')['Count'].sum().reset_index()
                result_df = result_df.sort_values(by='Count', ascending=False)

                bought_together = result_df['Count'].sum()
                bought_together_rate = bought_together * 100 / total_order if total_order > 0 else 0
                bought_alone_rate = (total_order - bought_together) * 100 / total_order

                if bought_together_rate >= input_threshold_value:
                    st.write(f"ASIN: {iterated_asin}")
                    st.write(f"Toplam Sipariş Sayısı: {total_order}")
                    st.write(f"Birlikte Satın Alma Oranı: {bought_together_rate:.2f}%")
                    st.write(f"Tek Başına Satın Alma Oranı: {bought_alone_rate:.2f}%")

                processed_asins.add(iterated_asin)
        # Web sitesini bir iframe içinde göster
        st.markdown("### Amazon ASIN Arama")
        components.iframe("https://amazon-asin.com/", height=500, scrolling=True)

def ana():
    st.sidebar.title("Sepet Analizi")
    sayfa = st.sidebar.radio("Sayfa Seçiniz:", ['Birlikte Satın Alınan Ürün Analizi', 'ASIN Analizi'])

    if sayfa == 'Birlikte Satın Alınan Ürün Analizi':
        beraber_satinalma_analizi()
    elif sayfa == 'ASIN Analizi':
        asin_analizi()

if __name__ == "__main__":
    ana()
