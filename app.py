from flask import Flask, render_template, request
import csv
from webscraping import scrape_flipkart, scrape_amazon

app = Flask(__name__)

# Function to read product prices from Amazon CSV
def read_amazon_prices_from_csv():
    amazon_prices = {}
    with open('amazon.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if(row['product_name']!='' and row['product_price']!=''):
                amazon_prices[row['product_name']] = [row['product_price'],row['product_link']]
    return amazon_prices

# Function to read product prices from Flipkart CSV
def read_flipkart_prices_from_csv():
    flipkart_prices = {}
    with open('flipkart.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if(row['product_name']!='' and row['product_price']!=''):
                if('ram' in row['product_ram']):
                    flipkart_prices[row['product_name']] = [row['product_price'].replace('â‚¹', ''),row['product_link'],row['product_ram'].split('ram')[0].strip()]
                else:
                    flipkart_prices[row['product_name']] = [row['product_price'].replace('â‚¹', ''),row['product_link'],'']
    return flipkart_prices

# Route for index page
@app.route('/')
def index():
    return render_template('index.html')

# Route for comparison page
@app.route('/compare')
def compare():
    product_name = request.args.get('product_name')
    product_storage = request.args.get('product_storage')
    product_ram = request.args.get('product_ram')
    product_price = request.args.get('product_price').split('-') #list

    search_term=product_name+' '+product_storage+' '+product_ram
    scrape_flipkart(search_term)
    scrape_amazon(search_term)
    
    amazon_prices = read_amazon_prices_from_csv()
    fk_prices = read_flipkart_prices_from_csv()
    print(amazon_prices)
    print(fk_prices)

    matching_amazon_products ={name: price for name, price in amazon_prices.items()  
                                if int(price[0].replace(',','')) in range(int(product_price[0]),int(product_price[1]))}

    matching_flipkart_products = {name: price for name, price in fk_prices.items()
                                if int(price[0].replace(',','').replace('₹',''))in range(int(product_price[0]),int(product_price[1]))}
    
    listC={}
    listD={}
    for name, detail in matching_flipkart_products.items():
        list=name.split("(")
        flipkart_name=list[0].strip()
        color=list[1]
        list2=color.split(",")
        flipkart_color=list2[0]
        for amazon_name, amazon_detail in matching_amazon_products.items():
            if flipkart_name in amazon_name and flipkart_color in amazon_name and (detail[2].replace(' ', '') in amazon_name or detail[2] in amazon_name):
                listC[name]=amazon_detail
                listD[name]=detail
                break
    print()
    print()
    print(listC)           
        
    return render_template('display.html', amazon_products=listC, flipkart_products=listD, search_term=product_name)

if __name__ == "__main__":
    app.run(debug=True)