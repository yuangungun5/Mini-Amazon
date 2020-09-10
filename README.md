# ECE 568 final project

## How to use our mini-amazon

1.cd into the docker-deploy directory

2.modify the upsAddress and worldAddress in ./amazon_sever/server.py (on the top
of the file)

3.run command: sudo docker-compose build

4.run command: sudo docker-compose up

5.go to the webpage of "vcm-xxxxx.vm.duke.edu:8000"

6.register and log in

7.start shopping by click "SHOP NOW" in the homepage or click "Home" on the 
header

8.choose the product you like and click the number of them

9.if you want to add it to your wish list, you can click "Add to List". Or if 
you want to buy the product this time, you can click "Add to Cart"

10.if you choose "Add to Cart", you need to put the number of products

11.Then you will come to the cart page, if you want to add more products in your
cart, you can click "Home" on the head to shop more products. Or you can click
"Checkout" button. There is a total price of your shopping on the button.

12.after clicking "Checkout" button, you need to input the destination address 
of your package. Click "submit" when you done

13.If your balance is not enough for the purchase, the system will redirect you
to the recharge page. And you will want to recharge some money in your account.
You also can visit recharge page in your account.
After success submission, our system will send you and email to confirm the 
order is created and you will come to the order page. You can also click 
"MyOrder" on the head to visit the order page.

14.on the order page, you can see the details of each order by clicking "order"
on each order block

15.on the order detail page, you will find the details of the order. If you want
to check the status of your package, click "Query Delivery"

16.you can modify your information on the "MyAccount" section

17.if you want to search for the product, you can use "Search" section and
input the name of the product, like "yogurt" to find the product