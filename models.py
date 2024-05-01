import sqlite3 
from cryptography.fernet import Fernet
import os

def get_security_key():
  return os.environ['SECURITY_KEY']

con = sqlite3.connect('printsplash.sqlite',check_same_thread=False) 
cur = con.cursor()

def is_secured(key):
  return key==os.environ["SECURITY_KEY"]

def encode_pass(password):
  pass_key = Fernet(os.environ['DECODING_KEY'].encode())
  new_pass = pass_key.encrypt(password.encode()).decode()
  return new_pass

def decode_pass(key):
  pass_key = Fernet(os.environ['DECODING_KEY'].encode())
  password = pass_key.decrypt(key.encode()).decode()
  return password


class designer:

  def __init__(self,email,nom,password):
    self.email = email.lower()
    self.password = encode_pass(password)
    self.nom = nom

  def save(self):
    cur.execute(f'insert into designer(email,nom,password) values("{self.email}","{self.nom}","{self.password}")')
    con.commit()
    
  @classmethod
  def get_designer(cls,email):
    cur.execute(f'select email,nom,password from designer where email ="{email.lower()}" ')
    des = cur.fetchone()
    if des is None:
      return None
    return cls(des[0],des[1],decode_pass(des[2])) 

  @classmethod
  def get_id(cls,email):
    cur.execute(f'select id from designer where email ="{email.lower()}" ')
    des = cur.fetchone()
    if des is None:
      return None
    return des[0] 
    
  @classmethod
  def get_myprofit(cls,id):
    cur.execute(f'select sum(qte*achat.prix),sum(qte) from achat join tshirt t on achat.tshirt = t.id where t.designer ="{id}"')
    des = cur.fetchone()
    if des is None:
      return None
    return des

  @classmethod
  def get_mydaystats(cls,date,id):
    cur.execute(f'select IFNULL(sum(qte),0),IFNULL(sum(qte*achat.prix),0) from achat join commade comm on commande_id=comm.id join tshirt t on achat.tshirt = t.id where t.designer ="{id}" and comm.date LIKE "{date}%" ;')
    des = cur.fetchone()
    if des is None:
      return None
    return des

  @classmethod
  def get_mybest(cls,id):
    cur.execute(f'select  tshirt,sum(qte),sum(qte)*achat.prix as total from achat join tshirt t on achat.tshirt = t.id  where t.designer ="{id}" group by achat.tshirt order by total desc LIMIT 3;')
    des = cur.fetchall()
    if des is None:
      return None
    return des

  @classmethod
  def get_alldesigners(cls):
    # cur.execute('select email,nom,password from designer')
    # cur.execute('select email,nom,(select ) from designer')
    cur.execute('select email,nom,(select IFNULL(sum(qte),0) from achat join tshirt t on achat.tshirt = t.id where t.designer = d.id) as qte from designer d order by qte desc')

    des = cur.fetchall()
    if des is None:
      return None
    return des

class Commande:

  def __init__(self,lieu,date,nom_client,carte,products):
    self.lieu = lieu 
    self.date = date
    self.nom_client = nom_client
    self.carte = carte 
    self.products = products
    

  def save(self):
    cur.execute(f'insert into commade(lieu,date,nom_client,carte_bancaire) values("{self.lieu}","{self.date}","{self.nom_client}",{self.carte})')
    commaid = cur.lastrowid
    for product in  self.products:
      cur.execute(f'insert into achat(commande_id,tshirt,qte,prix)  VALUES ({commaid},{product[0]},{product[1]},(select prix from tshirt where id={product[0]}))')
    con.commit()
    
  @classmethod
  def get_mysales(cls,id):
    cur.execute(f'select tshirt,qte,achat.prix from achat join tshirt t on achat.tshirt = t.id where t.designer ="{id}"')
    des = cur.fetchall()
    if des is None:
      return None
    return des 

  @classmethod
  def get_sales(cls):
    cur.execute('select tshirt,qte,t.prix from achat join tshirt t on achat.tshirt = t.id')
    des = cur.fetchall()
    if des is None:
      return None
    return des

  @classmethod
  def get_commsales(cls,cid):
    cur.execute('select tshirt,qte,t.prix from achat join tshirt t on achat.tshirt = t.id join commade c on achat.commande_id = c.id where c.id='+str(cid))
    des = cur.fetchall()
    if des is None:
      return None
    return des

  @classmethod
  def get_commands(cls):
    cur.execute('select id,lieu,date,nom_client from commade')
    des = cur.fetchall()
    if des is None:
      return None
    return des

  @classmethod
  def get_best(cls):
    cur.execute('select  tshirt,sum(qte),sum(qte)*achat.prix as total from achat join tshirt t on achat.tshirt = t.id group by achat.tshirt order by total desc LIMIT 3;')
    des = cur.fetchall()
    if des is None:
      return None
    return des
    
  @classmethod
  def get_daystats(cls,date):
    cur.execute(f'select IFNULL(sum(qte),0),IFNULL(sum(qte*achat.prix),0) from achat join commade comm on commande_id=comm.id join tshirt t on achat.tshirt = t.id where comm.date LIKE "{date}%" ;')
    des = cur.fetchone()
    if des is None:
      return None
    return des

  @classmethod
  def get_profit(cls):
    cur.execute('select sum(qte*achat.prix),sum(qte) from achat join tshirt t on achat.tshirt = t.id ')
    des = cur.fetchone()
    if des is None:
      return None
    return des

class tshirt:
  
  def __init__(self,prix,email):
    self.prix = prix
    self.designer_id = designer.get_id(email)

  def save(self):
    cur.execute(f'insert into tshirt(prix,designer) values({self.prix},{self.designer_id})')
    con.commit()

  @classmethod
  def get_tshirt(cls,id):
    cur.execute(f'select prix,designer from tshirt where id ={id}')
    des = cur.fetchone()
    if des is None:
      return None
    return des
  
  @classmethod
  def get_tshirts_of_designer(cls,id):
    try:
      cur.execute(f'select id,prix,(select count(*) from achat where tshirt=id) from tshirt where designer ={id}')
      des = cur.fetchall()
      if cur.rowcount == 0 :
        return None
    except:
      return None
      
    return des

  @classmethod
  def get_tshirts(cls):
    cur.execute('select id,prix,designer from tshirt ')
    des = cur.fetchall()
    if cur.rowcount == 0 :
      return None
    return des

  @classmethod
  def update_tshirt(cls,id,prix):
    cur.execute(f'update tshirt set prix={prix} where id={id}')
    con.commit()
    

  @classmethod
  def delete_tshirt(cls,id):
    cur.execute(f'delete from tshirt where id={id}')
    cur.execute(f'delete from achat where tshirt={id}')
    cur.execute(f'update tshirt set id=id-1 where id>{id}')
    cur.execute('UPDATE SQLITE_SEQUENCE SET seq = (select count(*) from tshirt) WHERE name = "tshirt"')
    os.remove(f"tshirts/tshirt{id}.png")
    os.remove(f"designs/tshirt{id}.png")
    os.system(f"./delscrpt {id}")
    con.commit()

  @classmethod
  def delete_all(cls):
    cur.execute('delete from tshirt') 
    cur.execute('UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = "tshirt"')
    os.system("rm tshirts/tshirt*.png")
    os.system("rm designs/tshirt*.png")
    con.commit()
    
  
  
def test():
    # from random import randint
    # for i in range(28,31):
    #   tshirt(randint(61,160),["salim.alaoui@gmail.com","salim@gmail.com"][randint(0,1)]).save()
    # return tshirt.get_tshirts_of_designer(designer.get_id())
    # cur.execute("select * from designer")
    # return cur.fetchall()
    return decode_pass(os.environ["ADMIN_KEY"])
    # pass
    # cur.execute("select * from designer")
    # designers = cur.fetchall()
    # for des in designers:
    #   print(des)
    # cur.execute('update designer set email="peace@gmail.com" where id=9')
    # cur.execute('update designer set nom="salim" where id=9')
    # cur.execute('update designer set password="gAAAAABlMVU1VpLEy9tShpBRiQZ8pC9JdzzMv-lwWwIYjH8O3NaqDxKz_xcsz0GyPO30izTArHhU8ZEcWNrJY5jBgt44Stuhcw==" where id=9')
    # cur.execute("select * from designer")
    # print(cur.fetchall())
    # con.commit()



def savetshirt(data):
    from PIL import Image , ImageChops
    from io import BytesIO
    import base64
    tshirt = Image.open("mockup.png")
    y =  int(data["y"]*tshirt.width)
    x =  int(data["x"]*tshirt.width)
    w =  int(data["w"]*tshirt.width)
    h =  int(data["h"]*tshirt.width)
    color = (int(data["color"][1:3],base=16),int(data["color"][3:5],base=16),int(data["color"][5:],base=16))
    blend =  data["blend"]
    tid = len(os.listdir("tshirts"))+1
  
    design = Image.open(BytesIO(base64.b64decode(data['img'][data['img'].find(";base64")+8:]))).resize((w,h)).convert('RGBA')
    design.save(f"designs/tshirt{tid}.png")
    # color_background = Image.new("RGBA",tshirt.size,color)
    tshirt = ImageChops.multiply(tshirt,Image.new("RGBA",tshirt.size,color))
    
    mask = ImageChops.multiply(Image.open("mask.png").crop((x,y,x+w,y+h)),Image.new("RGBA",tshirt.size,color)).convert('RGBA')
    # mask = tshirt.crop((x,y,x+w,y+h)).convert('RGBA')
  
    # tshirt = ImageChops.multiply(tshirt,color_background)
    if blend!="normal":
        if blend=="multiply":
            design = ImageChops.multiply(mask,design)
        elif blend=="screen":
            design = ImageChops.screen(mask,design)
        elif blend=="overlay":
            design = ImageChops.overlay(mask,design)
        elif blend=="lighten":
            design = ImageChops.lighter(mask,design)
        elif blend=="darken":
            design = ImageChops.darker(mask,design)
        elif blend=="difference":
            design = ImageChops.difference(mask.convert('RGB'),design.convert('RGB'))
        elif blend=="color-burn":
            design = ImageChops.soft_light(
              ImageChops.soft_light(
              ImageChops.soft_light
              (mask,design),design),design)
        elif blend=="hard-light":
            design = ImageChops.hard_light(mask,design)
        elif blend=="soft-light":
            design = ImageChops.soft_light(mask,design)
          
    mask.paste(design,(0,0),mask)
    t = tshirt.copy()
    tshirt.paste(mask,(x,y))
    tshirt = Image.alpha_composite(t, tshirt)
    tshirt.save(f"tshirts/tshirt{tid}.png")
    return {"response":"200","message":"Added"}
    

class message:

  def __init__(self,email,message,date):
    self.email = email.lower()
    self.message = message
    self.date = date

  def save(self):
    cur.execute(f'insert into message(email,message,date) values("{self.email}","{self.message}","{self.date}")')
    con.commit()
    
  @classmethod
  def get_messages(cls):
    cur.execute('select email,message,date from message ORDER BY id DESC')
    des = cur.fetchall()
    return des 

class AdminLog:
  def __init__(self,ip,agent,date):
    self.ip = ip
    self.agent = agent
    self.date = date
    
  def save(self):
    cur.execute(f'insert into adminlogs(ip,agent,date) values("{self.ip}","{self.agent}","{self.date}")')
    con.commit()

  @classmethod
  def get_admins(cls):
    cur.execute('select ip,agent,date from adminlogs ORDER BY id DESC')
    des = cur.fetchall()
    return des 

  @classmethod
  def is_admin(cls,key):
    return key==decode_pass(os.environ["ADMIN_KEY"])
