import world_amazon_pb2 as wa
import socket
import time
import threading
import select

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

import amazon_client_pb2 as client
from init_db import *
import queue

#modify the world address here!!!
worldAddress=("vcm-13666.vm.duke.edu", 23456)
#modify the ups address here!!!
upsAddress=("vcm-12415.vm.duke.edu",5000)

SEQ_NUM = 0
WAIT_ACK_QUEUE = []
WEB_QUEUE = queue.Queue()
UPS_QUEUE=queue.Queue()
clientAddress = ("0.0.0.0", 33333)

# read message with google buffer protocol, and turn it into a message buffer
def readClientRequest(sock):
    var_int_buff = b''
    while True:
        buf = sock.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = sock.recv(msg_len)
    return whole_message


def responseFromWorld(sock):
    message = readClientRequest(sock)
    world_response = wa.AResponses()
    world_response.ParseFromString(message)
    return world_response

def responseFromUps(sock):
    message = readClientRequest(sock)
    world_response = wa.UA_Responses()
    world_response.ParseFromString(message)
    return world_response


def waitACK(seqnum, message, sock):
    global WAIT_ACK_QUEUE
    
    while True:
        # receive from world
        wait = select.select([sock], [], [], 10)
        if wait[0]:
            world_response = responseFromWorld(sock)
            if not world_response.acks:
                print("no acks")
                print(world_response)
                break
            else:   
                for ack in world_response.acks:
                    print(f"receive ack: {ack}")
                    WAIT_ACK_QUEUE.remove(ack)
                    if ack == seqnum:
                        # return
                        return world_response
            
                    # check WAIT_ACK_QUEUE every 10 seconds
        if seqnum in WAIT_ACK_QUEUE:
            # send again
            print("resend")
            _EncodeVarint(sock.send, len(message), None)
            sock.send(message)

def replyACK(ackToSend, sock):
    replyToWorld = wa.ACommands()
    replyToWorld.acks.append(ackToSend)
    reply = replyToWorld.SerializeToString()
    _EncodeVarint(sock.send, len(reply), None)
    sock.send(reply)
    return

def sendMessage(Sock,message):
    sendTo = message.SerializeToString()
    _EncodeVarint(Sock.send, len(sendTo), None)
    Sock.send(sendTo)
    return sendTo

def getSeq_num():
    global SEQ_NUM
    SEQ_NUM+=1
    WAIT_ACK_QUEUE.append(SEQ_NUM)
    return SEQ_NUM


def purchaseMore(product_message, worldSock, conn):
    cursor = conn.cursor()
    purchaseFromWH = wa.ACommands()
    purchase = purchaseFromWH.buy.add()
    whnum = SEQ_NUM % 5 + 1    # random warehouse from 1 to 5
    PMflag = 0
    
    for _product in product_message.things:
        productID = _product.id
        sql = '''SELECT stock FROM website_stock WHERE warehouse_id = %s AND product_id = %s;'''
        cursor.execute(sql,(whnum, productID))
        curr_stock = cursor.fetchone()[0]
        count = _product.count
        thing = purchase.things.add()
        thing.id = _product.id
        thing.description = _product.description
        if (curr_stock <= count):
            # purchase more
             PMflag = 1
             thing.count = _product.count + 100
        else:
            thing.count = _product.count

    if PMflag == 1:
        # as long as one product does not have enough stock, purchase all
        # not enough: purchase count+100
        # enough: purchase count
        # else directly return to call truck
        purchase.seqnum = getSeq_num()
        purchase.whnum = whnum
        WAIT_ACK_QUEUE.append(purchase.seqnum)
        
        sendToWorld=sendMessage(worldSock,purchaseFromWH)
        order_id = product_message.orderid
        print(f"{order_id} purchase sent")
        print(purchase.seqnum)
        print("send world PurchaseMore")
        
        world_response = waitACK(purchase.seqnum, sendToWorld, worldSock)
        print("world responded")
        print(world_response)
        for PMresponse in world_response.arrived:
            for item in PMresponse.things:
                print(f"{item.description} stock +{item.count}")
                sql = '''UPDATE website_stock SET stock = stock + %s WHERE warehouse_id = %s AND product_id = %s;'''
                cursor.execute(sql, (item.count, whnum, item.id))
                conn.commit()
                print("+stock update")
                
        worldPMseq = PMresponse.seqnum
        print(f"world purchase more seq is {worldPMseq}")
        replyACK(worldPMseq, worldSock)
        print(f"send {worldPMseq} to world!")
        
    return whnum

def receiveFromWeb(clientSock):
    global WEB_QUEUE
    request = readClientRequest(clientSock)
    product_message = client.AOrder()
    product_message.ParseFromString(request)
    WEB_QUEUE.put(product_message)
    clientSock.close()
    print(product_message)

def receiveFromUps(clientSock):
    global UPS_QUEUE
    while True:
        request = readClientRequest(clientSock)
        product_message = wa.UA_Responses()
        product_message.ParseFromString(request)
        UPS_QUEUE.put(product_message)
        print(product_message)


def connectToWeb():
    serverSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    serverSock.bind(clientAddress)
    while True:
        print("Listening...")
        serverSock.listen()
        clientSock, clientAddr = serverSock.accept()
        try:
            t1 = threading.Thread(target=receiveFromWeb,args=(clientSock,))
            t1.start()
        finally:
            print("next accept:")

            
def callTruck(product_message, upsSock, conn,whnum):
    call=wa.UA_TruckCall()
    call.package_id=product_message.orderid
    for item in product_message.things:
        prod=wa.AProduct()
        prod.id=item.id
        prod.count=item.count
        prod.description=item.description
        call.products.append(prod)
    call.whnum=whnum
    call.owner_id=product_message.userid
    cursor=conn.cursor()
    sql = '''SELECT * FROM website_warehouse WHERE website_warehouse.id=%s;'''
    cursor.execute(sql,(whnum,))
    records = cursor.fetchall()
    for record in records:
        call.dest_x=record[1]  
        call.dest_y=record[2]
    call.seqnum=getSeq_num()
    message=wa.UA_Commands()
    message.acks.append(call.seqnum)
    message.truckCall.append(call)
    sendMessage(upsSock,message)
    print(message)

def goDeliver(product_message, upsSock, conn,truck_id):
    go=wa.UA_GoDeliver()
    go.truckid=truck_id
    go.packageid=product_message.orderid
    go.x=product_message.x
    go.y=product_message.y
    go.seqnum=getSeq_num()
    message=wa.UA_Commands()
    message.acks.append(go.seqnum)
    message.goDeliver.append(go)
    sendMessage(upsSock,message)
    print(message)

def updatePackage(conn,status,order_id):
    cursor = conn.cursor()
    sql = '''UPDATE website_order SET status=%s WHERE website_order.id = %s;'''
    cursor.execute(sql, (status,order_id,))
    conn.commit()
    
def getCurrentTime(conn):
    cursor = conn.cursor()
    sql = '''SELECT  CURRENT_TIMESTAMP;'''
    cursor.execute(sql)
    curr_time = cursor.fetchone()[0]
    return curr_time

def clientHandler(conn,worldSock,upsSock):
    while True:
        global SEQ_NUM
        global WEB_QUEUE
        if WEB_QUEUE.empty():
            continue
        print("start handling..")
        product_message=WEB_QUEUE.get()
        order_id = product_message.orderid

        #send world to purchase
        print("purchase")
        whnum = purchaseMore(product_message, worldSock, conn)        
        # amazon sends UPS to call truck for pack
        print("call truck")
        callTruck(product_message, upsSock, conn,whnum)
        # after truck: packing
        print("packing")
        updatePackage(conn,'packing',order_id)
        packProduct(worldSock,product_message,whnum,conn)
        # world: packed
        updatePackage(conn,'packed',order_id)
        #receive truck arrived from ups
        print("wait for truck")
        k=0
        while UPS_QUEUE.empty():
             k=1 
        truck_arr=UPS_QUEUE.get()
        truck_id=0
        for arrive in truck_arr.truckArrived:
            truck_id=arrive.truck_id
        #send load to world
        updatePackage(conn,'loading',order_id)
        loadProduct(worldSock,product_message,truck_id,whnum)
        updatePackage(conn,'loaded',order_id)
        #send godelivery to ups
        goDeliver(product_message, upsSock, conn,truck_id)
        updatePackage(conn,'delivering',order_id)
        #wait ups delivered
        print("wait for delivery")
        while UPS_QUEUE.empty():
            k=2
        deliver=UPS_QUEUE.get()
        updatePackage(conn,'delivered',order_id)

        
def packProduct(worldSock,products,whnum,conn):    
    print(f"Sending pack to world...")
    cursor = conn.cursor()
    pack=wa.APack()
    pack.whnum= whnum
    for item in products.things:
        product = wa.AProduct()
        product = pack.things.add()
        product.id = item.id
        product.description = item.description
        product.count = item.count
       
        #print(f"{item.description} stock -{item.count}")
        sql = '''UPDATE website_stock SET stock = stock - %s WHERE warehouse_id = %s AND product_id = %s;'''
        cursor.execute(sql, (item.count, whnum, item.id))
        conn.commit()
        #print("-stock update")
    pack.shipid=products.orderid
    pack.seqnum=getSeq_num()
    pack_command=wa.ACommands()
    pack_command.topack.append(pack)
    send_pack=sendMessage(worldSock,pack_command)
    print(pack_command)
    print(f"sent to the world")
    pack_response = waitACK(pack.seqnum, send_pack, worldSock)
    print(f"receive from the world")
    print(pack_response)
    packed=responseFromWorld(worldSock)
    print(packed)
    for p in packed.ready:
        replyACK(p.seqnum, worldSock)
        

def loadProduct(worldSock,product,truck_id,whnum):
    load=wa.APutOnTruck()
    load.whnum=whnum
    load.truckid=truck_id
    load.shipid=product.orderid
    load.seqnum=getSeq_num()
    load_command=wa.ACommands()
    load_command.load.append(load)
    send_load=sendMessage(worldSock,load_command)
    print(load_command)
    print(f"sent to the world")
    load_response = waitACK(load.seqnum, send_load, worldSock)
    print(load_response)
    loaded=responseFromWorld(worldSock)
    print(loaded)
    replyACK(load.seqnum, worldSock)

    
def SocketServer(conn,ups_sock):
    #receive ups connect
    ua_connect=readClientRequest(ups_sock)
    ua_c=wa.UA_Connect()
    ua_c.ParseFromString(ua_connect)
    print(ua_c.worldid)
    
    first=wa.AConnect()
    first.worldid=ua_c.worldid
    first.isAmazon=True
    print(first)

    CreateTable("WH", conn)
    cursor = conn.cursor()
    InitWH(conn)
    InitStock(conn)

    sql = '''SELECT * FROM website_warehouse;'''
    cursor.execute(sql)
    records = cursor.fetchall()
    for row in records:
        initWH = first.initwh.add()
        initWH.id = row[0]
        initWH.x = row[1]
        initWH.y = row[2]
        print(f"{row[0]}  {row[1]}  {row[2]}")
    
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(worldAddress)

    sendMessage(s,first)
    print("send connect and init")
    
    whole_message = readClientRequest(s)
    m=wa.AConnected()
    m.ParseFromString(whole_message)
    print(m)

    try:
        t1 = threading.Thread(target=connectToWeb,args=())
        t2 = threading.Thread(target=clientHandler,args=(conn,s,ups_sock))
        t3 = threading.Thread(target=receiveFromUps,args=(ups_sock,))
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()
    finally:
        print('close')
        s.close()

def upsServer():
    upsSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    upsSock.connect(upsAddress)
    return upsSock
        
def Main():
    conn = connect_db()
    CreateTable("PRODUCT", conn)
    InitProduct(conn)
    ups_sock=upsServer()
    SocketServer(conn,ups_sock)


if __name__ == '__main__':
    Main()
