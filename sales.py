import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import plotly.express as px
# import matplotlib.pyplot as plt

if "step" not in st.session_state: st.session_state['step'] = 0

if "show_graph" not in st.session_state: st.session_state.show_graph=False

# engine = create_engine('mysql+mysqlconnector://shiva:lion@localhost/PR')


st.set_page_config(page_title="Sales dashboard",page_icon="📊",layout="wide")
st.title("📊 Sales Analysis Dashboard")
st.markdown("This dashboard shows sales, revenue and product analysis.")


df=pd.read_excel(r"D:\Excel\sales analisys.xlsx")


# Data cleaning.............................................

if st.session_state['step'] == 0:
    
    df.columns =df.columns.str.strip().str.lower().str.replace(" ","_")
    df['order_date'] = df['order_date'].astype(str).str.strip()
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df = df.dropna(subset=['order_date'])
    

    df['product_name'] = df['product_name'].astype(str).str.strip()

    df= df.drop_duplicates()


    st.subheader("🧹 Data Cleaning Control Panel")
    col1,col2,col3=st.columns(3)
    date_action = col1.radio( "1)-If ORDER DATE is missing, what should we do?",["Ignore", "Delete row", "Replace with today date"])
    
    price_action = col2.radio("2)-If PRICE is missing, what should we do?",["Ignore", "Delete row", "Replace with average price"])
   
    quantity_action = col3.radio("3)-If QUANTITY is missing, what should we do?",["Ignore", "Delete row", "Replace with 1"])

    
    df['order_date']= pd.to_datetime(df['order_date'],errors='coerce')


    if date_action =='Delete row':
        df=df.dropna(subset=['order_date'])
    elif date_action == 'Replace with today date':
        df['order_date']=df['order_date'].fillna(pd.Timestamp.today())


    if price_action == 'Delete row':
        df= df.dropna(subset=['price'])

    elif price_action=='Replace with average price':
        df['price']= df['price'].fillna(df['price'].mean())


    if quantity_action == 'Delete row':
        df = df.dropna(subset=['quantity'])

    elif quantity_action == 'Replace with 1':
        df['quantity'] = df['quantity'].fillna(1)


    st.write("\n✅ Data Cleaning Completed Successfully")


    st.write(df.head())
    if st.button("Go to Filtering & Analisys->"):
        st.session_state['step']=1

    st.session_state['cleaned_df']=df

    df.columns = df.columns.str.strip()





# Data filtering .........................................

elif st.session_state['step'] == 1:

    df=st.session_state['cleaned_df']

    col1,col2=st.columns(2)

    start_order_id_input = col1.number_input("Start order id :",min_value=0,step=1,format="%d")
    end_order_id_input = col2.number_input("enter ending order id :",min_value=0,step=1,format="%d")

    col3,col4=st.columns(2)
    min_price_input = col3.number_input("Enter minimum price :",min_value=0.0,step=1.0)
    max_price_input = col4.number_input("Enter maximum price :",min_value=0.0,step=1.0)
    
    col5,col6=st.columns(2)
    start_date_input= col5.date_input("Start date : ",value=None, )
    end_date_input = col6.date_input("End date : ",value=None, )



    start_order_id= int(start_order_id_input) if start_order_id_input else None
    end_order_id= int(end_order_id_input) if end_order_id_input else None
    min_price= float(min_price_input) if min_price_input else None
    max_price= float(max_price_input) if max_price_input else None
    start_date= pd.to_datetime(start_date_input,errors='coerce') if start_date_input else None
    end_date = pd.to_datetime(end_date_input, errors='coerce') if end_date_input else None


    if start_order_id is not None and end_order_id is not None:
        df= df[(df['order_id']>= start_order_id) & (df ['order_id']<= end_order_id)]
    elif start_order_id is not None:
        df=df[df['order_id']>=start_order_id]
    elif end_order_id is not None:
        df=df[df['order_id']<= end_order_id]


    if min_price is not None and max_price is not None:
        df = df[(df['price']>=min_price) & (df['price']<= max_price)]

    elif min_price is not None:
        df = df[df['price'] >= min_price]
    elif max_price is not None:
        df = df[df['price'] <= max_price]

    if start_date and end_date:
        df = df[(df['order_date'] >= start_date) & (df['order_date'] <= end_date)]
    elif start_date:
        df = df[df['order_date'] >= start_date]
    elif end_date:
        df = df[df['order_date'] <= end_date]



# Data analysis...............................................



    st.write("\n--- DATA ANALYSIS ---")

    # 1. Total Orders
    total_orders = df.shape[0]
    st.write("Total Orders:", total_orders)

    # 2. Total Quantity Sold
    total_quantity = df['quantity'].sum()
    st.write("Total Quantity Sold:", total_quantity)

    # 3. Total Revenue
    df['revenue'] = df['quantity'] * df['price']
    total_revenue = df['revenue'].sum()
    st.write("Total Revenue:", total_revenue)

    # 4. Average Order Value
    average_order_value = df['revenue'].mean()
    st.write("Average Order Value:", average_order_value)

    # 5. Top Selling Product (by quantity)
    colA,colB=st.columns(2)

    top_product = df.groupby('product_name')['quantity'].sum().sort_values(ascending=False)
    colA.write("Top Selling Products:")
    colA.write(top_product)

    # 6. Revenue by Product 
    revenue_by_product = df.groupby('product_name')['revenue'].sum().sort_values(ascending=False)
    colB.write("Revenue by Product:")
    colB.write( revenue_by_product)


    col1,col2,col3=st.columns([1,6,1])
    if col1.button("<- previous"):
        st.session_state['step']= 0
    if col3.button("Go for graph builder ->"):
        st.session_state['step']= 2
        st.rerun()

# Data graph------------------------------------------------


if st.session_state['step']== 2:
    df= st.session_state['cleaned_df']
    st.session_state.show_graph =False

    st.subheader("Graph Builder")
    
    df['revenue']=df['price']*df['quantity']

    chart_type = st.selectbox("Select Chart Type",["Bar Chart", "Line Chart", "Pie Chart"])

    x_col = st.selectbox("Select X Axis Column", df.columns)

    numaric_cols=df.select_dtypes(include=['int64','float64']).columns

    y_col = st.selectbox("Select Y Axis Column",numaric_cols)
    
    if st.button('<-previous'):
        st.session_state['step']=1
        st.rerun()

    if st.button("Generate Graph"):
        st.session_state.show_graph = True

    if st.session_state.get("show_graph",False):
        if chart_type=="Bar Chart" :
            fig =px.bar(df,x=x_col,y=y_col)
            st.plotly_chart(fig,use_container_width=True)

        elif chart_type=="Line Chart":
            fig =px.line(df,x=x_col,y=y_col)
            st.plotly_chart(fig,use_container_width=True)

        elif chart_type=="Pie Chart":
            fig =px.pie(df, names=x_col,values=y_col)
            st.plotly_chart(fig,use_container_width=True)

    


  
# df.to_sql('sales', con=engine, if_exists='replace', index=False)





