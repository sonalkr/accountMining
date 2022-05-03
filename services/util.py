from ast import Try
import locale
from tkinter import INSERT
import traceback
from db import getDb, getDgReadOnly


def getorCreateAgentId(agent_name) -> int:
    con = getDb()
    db = con.cursor()
    db.execute(f"select id from agent where agent_name = '{agent_name}' COLLATE NOCASE;")
    row = db.fetchone()
    id = 0
    if(row == None):
        db.execute(f"INSERT INTO agent (agent_name) VALUES('{str(agent_name).upper()}')")
        id = db.lastrowid
        con.commit()
    else:
        con.close()
        id = row[0]
    con.close()
    return id


def getListOfAgentName() -> int:
    con = getDb()
    db = con.cursor()
    try:
        db.execute(f"""
            SELECT agent_name FROM agent
            ORDER BY
                    agent_name ASC
        """)
        row = db.fetchall()
    except:
        con.close()
        traceback.print_exc()
        return list()
    con.commit()
    con.close()
    return row


def getorCreateMaterialShippingId(is_material, material_name) -> int:
    con = getDb()
    db = con.cursor()
    db.execute(f"select id from material where material_name = '{material_name}' COLLATE NOCASE;")
    row = db.fetchone()
    id = 0
    if(row == None):
        if is_material:
            db.execute(f"INSERT INTO material (typeof, material_name) VALUES('material','{str(material_name).upper()}')")
        else:
            db.execute(f"INSERT INTO material (typeof, material_name) VALUES('shipping_address','{str(material_name).upper()}')")
        id = db.lastrowid
        con.commit()
    else:
        con.close()
        id = row[0]
    con.close()
    return id

def getMaterialShippingId( material_name) -> int:
    con = getDb()
    db = con.cursor()
    db.execute(f"select id from material where material_name = '{material_name}' COLLATE NOCASE;")
    row = db.fetchone()
    id = 0
    if row != None:
        con.close()
        id = row[0]
    con.close()
    return id


def getorCreateSiteId(site_name) -> int:
    con = getDb()
    db = con.cursor()
    db.execute(f"select id from site_ where site_name = '{site_name}' COLLATE NOCASE;")
    row = db.fetchone()
    id = 0
    if(row == None):
        db.execute(f"INSERT INTO site_ (site_name) VALUES('{str(site_name).upper()}')")
        id = db.lastrowid
        con.commit()
    else:
        con.close()
        id = row[0]
    con.close()
    return id

def getMaterialShippingId(material_name) -> int:
    con = getDb()
    db = con.cursor()
    db.execute(f"select id from material where material_name = '{str(material_name).upper()}' COLLATE NOCASE;")
    row = db.fetchone()
    id = 0
    if(row == None):
        con.close()
        return id
    id = row[0]
    con.close()
    return id

def getMaterialShippingNameById(id_material) -> int:
    con = getDb()
    db = con.cursor()
    db.execute(f"select material_name from material where id = '{id_material}';")
    row = db.fetchone()
    material_name = ""
    if(row == None):
        con.close()
        return material_name
    material_name = row[0]
    con.close()
    return material_name

def getUnitId(unit_name):
    con = getDb()
    db = con.cursor()
    db.execute(f"""
            SELECT id FROM unit
            where unit_name = '{unit_name}' COLLATE NOCASE""")
    row = db.fetchone()
    id = 0
    if(row == None):
        con.close()
        return id
    id = row[0]
    con.close()
    return id


def verifyMaterialAndShippingLookup(material_name):
    con = getDb()
    db = con.cursor()
    db.execute(f"""SELECT material_name FROM lookupTableMaterial l
        INNER JOIN material m
            ON l.id_material = m.id
        and lookup_material_name = '{material_name}' COLLATE NOCASE""")
    row = db.fetchone()
    material_name = ""
    if(row == None or row[0] == None):
        con.close()
        return material_name
    material_name = row[0]
    con.close()
    return material_name


def verifyAccountLookup(account_name):
    con = getDb()
    db = con.cursor()
    db.execute(f"""SELECT account_name FROM lookupTableAccount l
        INNER JOIN account a
            ON l.id_account = a.id
        and lookup_account_name = '{account_name}' COLLATE NOCASE""")
    row = db.fetchone()
    return_account_name = ""
    if(row == None or row[0] == None):
        con.close()
        return return_account_name
    return_account_name = row[0]
    con.close()
    return return_account_name

def createAccountLookup(id_account, lookup_account_name):
    con = getDb()
    db = con.cursor()
    db.execute(
        f"""INSERT INTO lookupTableAccount (id_account, lookup_account_name)
        VALUES({id_account},'{str(lookup_account_name).upper()}')""")
    con.commit()
    con.close()

def getListOfIDMaterialName():
    con = getDb()
    db = con.cursor()
    try:
        db.execute(f"""
            SELECT id, material_name FROM material
            WHERE typeof = "material"
            ORDER BY
                material_name ASC
        """)
        row = db.fetchall()
    except:
        con.close()
        traceback.print_exc()
        return list()
    con.commit()
    con.close()
    return row

def getListOfIDShippingAddress():
    con = getDb()
    db = con.cursor()
    try:
        db.execute(f"""
            SELECT id, material_name FROM material
            WHERE typeof = "shipping_address"
            ORDER BY
                material_name ASC
        """)
        row = db.fetchall()
    except:
        con.close()
        traceback.print_exc()
        return list()
    con.commit()
    con.close()
    return row


def getListOfMaterialName():
    con = getDb()
    db = con.cursor()
    try:
        db.execute(f"""
            SELECT material_name FROM material
            ORDER BY
                material_name ASC
        """)
        row = db.fetchall()
    except:
        con.close()
        traceback.print_exc()
        return list()
    con.commit()
    con.close()
    return row

def createMaterialLookup(id_material, lookup_material_name):
    con = getDb()
    db = con.cursor()
    db.execute(
        f"""INSERT INTO lookupTableMaterial (id_material, lookup_material_name)
        VALUES({id_material},'{str(lookup_material_name).upper()}')""")
    con.commit()
    con.close()


def noneToBlank(arg):
    if arg:
        return arg
    return ""

def blankCurrencyFormat(arg):
    locale.setlocale(locale.LC_MONETARY, 'en_IN')
    if arg:
        return locale.currency(arg, grouping=True,symbol="")
    return ""

def convertProperNegative(amount):
    if amount[-1] == "-":
        return "-"+amount[:-1]
    return amount
def zeroCurrencyFormat(arg):
    locale.setlocale(locale.LC_MONETARY, 'en_IN')
    if arg:
        amount = locale.currency(arg, grouping=True,symbol="")
        amount = convertProperNegative(amount=amount)
        return amount
    return 0


def getFirstAccountName():
    con = getDb()
    db = con.cursor()
    try:
        db.execute(f"""
            SELECT account_name FROM account
        """)
        row = db.fetchone()
    except:
        con.close()
        traceback.print_exc()
        return False
    con.commit()
    con.close()
    return row