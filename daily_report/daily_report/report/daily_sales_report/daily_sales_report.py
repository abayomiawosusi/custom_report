# Copyright (c) 2022, abayomi.awosusi@sgatechsolutions.com and contributors
# For license information, please see license.txt

# import frappe
import calendar
import copy
from collections import OrderedDict
import datetime
import json
import frappe
from frappe import _, qb, scrub
from frappe.query_builder import CustomFunction
from frappe.query_builder.functions import Max
from frappe.utils import date_diff, flt, getdate
from erpnext.controllers.queries import get_match_cond
from erpnext.stock.utils import get_incoming_rate
from frappe.utils import cint, flt

def execute(filters=None):
    if not filters:
        return [], [], None, []

    #validate_filters(filters)

    #gross_profit_data = GrossProfitGenerator(filters)
    columns = []
    #columns = get_columns(filters)
    
    #data = get_merged_dataongrossprofls(filters,gross_profit_data.si_list)
    data = []
    if not data:
        return [], [], None, []
    
    return columns, data

def validate_filters(filters):
    cmonth = filters.get("month")

    if not cmonth:
        frappe.throw(_("Please select a month to generate report."))
    

def get_conditions(filters):
    conditions = ""
    
    if filters.get("month"):
        long_month_name = filters.get("month")
        datetime_object = datetime.datetime.strptime(long_month_name, "%B")
        month_number = datetime_object.month
        conditions += " MONTH(si.posting_date) = " + str(month_number)

    if filters.get("year"):
        conditions += " and YEAR(si.posting_date) = %(year)s"	

    return conditions

def get_merged_dataongrossprofls(filters,si_list):    
    workdaysinmth = []
    long_month_name = filters.get("month")
    datetime_object = datetime.datetime.strptime(long_month_name, "%B")
    month_number = datetime_object.month
    cal= calendar.Calendar()
    i=0
    lastwkdayincurrper = 0
    for x in cal.itermonthdays2(int(filters.get("year")), month_number):
        if ((x[0] != 0) and (x[1] < 7)):
            #print(x)   
            temparr = list((x[0],x[1],))
            workdaysinmth.append(temparr)
            i=i+1
            lastwkdayincurrper = x[0]
    #print(workdaysinmth)
    
    datamg = get_corrdataingplistwithcstcnt(si_list,workdaysinmth,lastwkdayincurrper,filters)

    return datamg

def get_corrdataingplist(lstdata,workdaysinmth,lastwkdayincurrper,filters):
    data5 = []
    stopt = 0
    month_number = 0
    curryr = 0
    prevyr = 0
    cumsalesmtd1 = 0
    cumsalesmtd2 = 0
    if filters.get("month"):
        long_month_name = filters.get("month")
        datetime_object = datetime.datetime.strptime(long_month_name, "%B")
        month_number = datetime_object.month
        curryr = int(filters.get("year"))
        prevyr = curryr -1
    for y in workdaysinmth:
        salesday = y[0]
        salesdate = datetime.datetime(curryr, month_number, salesday)
        prevsalesdate = datetime.datetime(prevyr, month_number, salesday)
        salesdayinwords = salesdate.strftime("%A")
        cumnoofinv1 = 0
        cumsales1 = 0
        cumgrossavg1 = 0
        cumnoofinv2 = 0
        cumsales2 = 0
        cumgrossavg2 = 0
        dategrossprf = 0.0
        dategrossprf2 = 0.0
        dategrossprfamt = 0.0
        dategrossprfamt2 = 0.0
        for row in lstdata:
            dayno1 = 1
            if ( (row["indent"]==0.0) and ((row["posting_date"]).strftime("%Y-%m-%d")==salesdate.strftime("%Y-%m-%d"))):
                cumnoofinv1 += 1
                cumsales1 += row["base_net_amount"]
                cumsalesmtd1 += row["base_net_amount"] 
                dategrossprf += row["gross_profit_percent"]
                dategrossprfamt += row["gross_profit"]
                dayno_object1 = datetime.datetime.strptime(str(row["posting_date"]), "%Y-%m-%d")
                dayno_object = dayno_object1.strftime("%d")
                dayno1 = int(str.lstrip(dayno_object))
            try:        
                cumgrossavg1 = dategrossprf/cumnoofinv1 
            except ZeroDivisionError:
                cumgrossavg1 = 0 

            dayno_object2 = datetime.datetime.strptime(str(row["posting_date"]), "%Y-%m-%d")
            dayno_object2 = dayno_object2.strftime("%d")
            dayno2 = int(str.lstrip(dayno_object2))
            prevdateyr = (row["posting_date"]).strftime("%Y")
            if ( (row["indent"]==0.0) and (int(prevdateyr) == prevyr) and (dayno2 == salesday)):
                cumnoofinv2 += 1
                cumsales2 += row["base_net_amount"]
                cumsalesmtd2 += row["base_net_amount"]  
                dategrossprf2 += row["gross_profit_percent"]
                dategrossprfamt2 += row["gross_profit"]
                stopt = dayno2
                
            #check for last lines that maybe left after loop and sum up
            if ( (row["indent"]==0.0) and (int(prevdateyr) == prevyr) and (dayno1 == lastwkdayincurrper) and (dayno2 > dayno1)):
                cumnoofinv2 += 1
                cumsales2 += row["base_net_amount"]
                cumsalesmtd2 += row["base_net_amount"]  
                dategrossprf2 += row["gross_profit_percent"]
                dategrossprfamt2 += row["gross_profit"]
                stopt = dayno2
            try:        
                cumgrossavg2 = dategrossprf2/cumnoofinv2 
            except ZeroDivisionError:
                cumgrossavg2 = 0       
        if ((cumnoofinv1 > 0) or (cumnoofinv2>0)) :    
            data5.append({"date":salesdate,"day":salesdayinwords,"noofinv":cumnoofinv1,"sales":cumsales1,"salesmtd":cumsalesmtd1,"gross":cumgrossavg1,"noofinv2":cumnoofinv2,"sales2":cumsales2,"salesmtd2":cumsalesmtd2,"gross2":cumgrossavg2})
        #data5.append({"day":salesdayinwords,"date":salesdate,"noofinv":cumnoofinv1,"sales":"{:,}".format(cumsales1),"salesmtd":cumsalesmtd1,"gross":'{:.2f}%'.format(cumgrossavg1),"noofinv2":cumnoofinv2,"sales2":"{:,}".format(cumsales2),"salesmtd2":cumsalesmtd2,"gross2":'{:.2f}%'.format(cumgrossavg2,2)})
                
    
    #print(data5)
    return data5    

def get_corrdataingplistwithcstcnt(lstdata,workdaysinmth,lastwkdayincurrper,filters):
    data5 = []
    data6 = []
    cstcnt = [] # get function to fetch cost centers
    #cstcnt = frappe.db.get_list("Cost Center")
    cstcnt0 = frappe.db.get_list("Cost Center",pluck='name',filters={'company': filters.get("company"),'is_group':0})
    # change the order of cost center this is customized for this client
    #specify order here 02, 03, 01, 06
    #cstorder = []
    if filters.cost_center:
        cstcnt0.clear()
        ccc = filters.cost_center
        for cc in ccc:
            cstcnt0.append(cc)

    cstorder = ['02', '03', '06', '01']
    
    i = 0
    while(i<len(cstorder)):
        for cstr in cstcnt0:
            if (cstr.startswith(cstorder[i])):
                cstcnt.append(cstr)
        i+=1
        
    # if created cost centers increase
    if ((len(cstorder)<len(cstcnt0)) and (len(cstcnt)>0) ):
        for cstr2 in cstcnt0:
            cstfound = False
            for m in cstcnt:
                if (m==cstr2):
                    cstfound = True
            if (cstfound == False):
                 cstcnt.append(cstr2)         

    if (len(cstcnt)==0):
       cstcnt = cstcnt0 

    #cstcnt = frappe.db.get_list("Cost Center",pluck='name',filters={'company': filters.get("company")})
    cclength = len(cstcnt)
    #print(cclength)
    #print(cstcnt)
    stopt = 0
    month_number = 0
    curryr = 0
    prevyr = 0
    cumsalesmtd1 = 0
    cumsalesmtd2 = 0
    grossprfmtd1 = 0.0
    grossprfmtd2 = 0.0
    grossprfmtdcum1 = 0.0
    grossprfmtdcum2 = 0.0
    cumgrossprfmtd1 = 0.0
    cumgrossprfmtd2 = 0.0
    daysoftxns1 = 0
    daysoftxns2 = 0
    
    grossprfamt1 = 0.0
    grossprfamt2 = 0.0

    cumsales3 = []
    cumnoofinv3 = []
    cumsalesmtd3 = []
    dategrossprf3 = []
    cumgrossavg3 = []

    dategrossprfamt3 = []

    cumgrossmtd3 = []
    daysoftxns3 = []
    cumgrossprfmtd3 = []
    grossprfmtd3 = [] 

    grossprfamt3 = []
    grossprfmtdcum3 = []
    #cumsales4 = []
    #cumnoofinv4 = []
    #cumsalesmtd4 = []
    #dategrossprf4 = []
    #cumgrossavg4 = []
    i = 0
    while(i<cclength):
        cumsales3.append(0)
        cumnoofinv3.append(0)
        cumsalesmtd3.append(0)
        dategrossprf3.append(0.0)
        cumgrossavg3.append(0)

        cumgrossmtd3.append(0)
        daysoftxns3.append(0)
        cumgrossprfmtd3.append(0)
        grossprfmtd3.append(0.0)

        grossprfamt3.append(0)

        dategrossprfamt3.append(0)
        grossprfmtdcum3.append(0.0)
        #cumsales4.append(0)
        #cumnoofinv4.append(0)
        #cumsalesmtd4.append(0)
        #dategrossprf4.append(0.0)
        #cumgrossavg4.append(0)
        i+= 1
     
    if filters.get("month"):
        long_month_name = filters.get("month")
        datetime_object = datetime.datetime.strptime(long_month_name, "%B")
        month_number = datetime_object.month
        curryr = int(filters.get("year"))
        prevyr = curryr -1
    for y in workdaysinmth:
        salesday = y[0]
        salesdate = datetime.datetime(curryr, month_number, salesday)
        #prevsalesdate = datetime.datetime(prevyr, month_number, prevsalesday)
        salesdayinwords = salesdate.strftime("%A")
        cumnoofinv1 = 0
        cumsales1 = 0
        cumgrossavg1 = 0
        cumnoofinv2 = 0
        cumsales2 = 0
        cumgrossavg2 = 0
        dategrossprf = 0.0
        dategrossprf2 = 0.0

        dategrossprfamt = 0.0
        dategrossprfamt2 = 0.0
        for i in range(cclength):
            cumsales3[i] = 0
            cumnoofinv3[i] = 0
            cumgrossavg3[i] = 0
            dategrossprf3[i]= 0.0

            dategrossprfamt3[i]= 0.0
            #cumsales4[i] = 0
            #cumnoofinv4[i] = 0
            #cumgrossavg4[i] = 0
            #dategrossprf4[i]= 0.0

        for row in lstdata:
            dayno1 = 1
            if ( (row["indent"]==0.0) and ((row["posting_date"]).strftime("%Y-%m-%d")==salesdate.strftime("%Y-%m-%d"))):
                cumnoofinv1 += 1
                cumsales1 += row["base_net_amount"]
                cumsalesmtd1 += row["base_net_amount"] 
                dategrossprf += row["gross_profit_percent"]

                dategrossprfamt += row["gross_profit"]
                grossprfmtdcum1 += row["gross_profit"]
                
                dayno_object1 = datetime.datetime.strptime(str(row["posting_date"]), "%Y-%m-%d")
                dayno_object = dayno_object1.strftime("%d")
                dayno1 = int(str.lstrip(dayno_object))

                for i in range(cclength):
                    if(cstcnt[i] == row["cost_center"]): 
                        cumnoofinv3[i] += 1
                        cumsales3[i] += row["base_net_amount"]
                        cumsalesmtd3[i] += row["base_net_amount"]
                        dategrossprf3[i] += row["gross_profit_percent"]

                        dategrossprfamt3[i] += row["gross_profit"]
                        grossprfmtdcum3[i] += row["gross_profit"]

            #try:        
            #    cumgrossavg1 = dategrossprf/cumnoofinv1 
            #except ZeroDivisionError:
            #    cumgrossavg1 = 0 
            
            #for i in range(cclength):
            #    cumgrossavg3[i] = 0
            #    if (dategrossprf3[i]!=0):
            #        cumgrossavg3[i] = dategrossprf3[i]/cumnoofinv3[i] 
           
                

            dayno_object2 = datetime.datetime.strptime(str(row["posting_date"]), "%Y-%m-%d")
            dayno_object2 = dayno_object2.strftime("%d")
            dayno2 = int(str.lstrip(dayno_object2))
            prevdateyr = (row["posting_date"]).strftime("%Y")
            if ((row["indent"]==0.0) and (int(prevdateyr) == prevyr) and (dayno2 == salesday)):
                cumnoofinv2 += 1
                cumsales2 += row["base_net_amount"]
                cumsalesmtd2 += row["base_net_amount"]  
                dategrossprf2 += row["gross_profit_percent"]
                stopt = dayno2
            
                dategrossprfamt2 += row["gross_profit"]
                grossprfmtdcum2 += row["gross_profit"]

                #for i in range(cclength):
                #    if(cstcnt[i] == row["cost_center"]): 
                #        cumnoofinv4[i] += 1
                #        cumsales4[i] += row["base_net_amount"]
                #        cumsalesmtd4[i] += row["base_net_amount"]
                #        dategrossprf4[i] += row["gross_profit_percent"]
                #print("stopt0")
            #check for last lines that maybe left after loop and sum up
            elif ( (row["indent"]==0.0) and (int(prevdateyr) == prevyr) and (dayno1 == lastwkdayincurrper) and (dayno2 > dayno1)):
                cumnoofinv2 += 1
                cumsales2 += row["base_net_amount"]
                cumsalesmtd2 += row["base_net_amount"]  
                dategrossprf2 += row["gross_profit_percent"]
                stopt = dayno2

                dategrossprfamt2 += row["gross_profit"]
                grossprfmtdcum2 += row["gross_profit"]

                #for i in range(cclength):
                #    if(cstcnt[i] == row["cost_center"]): 
                #        cumnoofinv4[i] += 1
                #        cumsales4[i] += row["base_net_amount"]
                #        cumsalesmtd4[i] += row["base_net_amount"]
                #        dategrossprf4[i] += row["gross_profit_percent"]
            #try:        
            #    cumgrossavg2 = dategrossprf2/cumnoofinv2 
            #except ZeroDivisionError:
            #    cumgrossavg2 = 0   

            #for i in range(cclength):
            #    cumgrossavg4[i] = 0
            #    if (dategrossprf4[i]!=0):
            #        cumgrossavg4[i] = dategrossprf4[i]/cumnoofinv4[i]    
        
        try:        
            cumgrossavg1 = (dategrossprfamt/cumsales1)*100 
        except ZeroDivisionError:
            cumgrossavg1 = 0

        try:        
            cumgrossavg2 = (dategrossprfamt2/cumsales2)*100 
        except ZeroDivisionError:
            cumgrossavg2 = 0     

        for i in range(cclength):
            cumgrossavg3[i] = 0
            if (dategrossprfamt3[i]!=0):
                cumgrossavg3[i] = (dategrossprfamt3[i]/cumsales3[i])*100
            
        try:    
            grossprfmtd1 = (grossprfmtdcum1/cumsalesmtd1)*100
        except ZeroDivisionError:
            grossprfmtd1 = grossprfmtd1
        try:
            grossprfmtd2 = (grossprfmtdcum2/cumsalesmtd2)*100
        except ZeroDivisionError:
            grossprfmtd2 = grossprfmtd2

        if ((cumnoofinv1 > 0) or (cumnoofinv2>0)) : 
        #if ((cumnoofinv1 > 0)) :
            if (cumnoofinv1>0) :
                cumgrossprfmtd1 += cumgrossavg1
                daysoftxns1 += 1
                #grossprfmtd1 = cumgrossprfmtd1/daysoftxns1
            if (cumnoofinv2>0) :
                cumgrossprfmtd2 += cumgrossavg2
                daysoftxns2 += 1
                #grossprfmtd2 = cumgrossprfmtd2/daysoftxns2

            cstdict = {"date":salesdate,"day":salesdayinwords}   
            data5.append({"date":salesdate,"day":salesdayinwords,"noofinv":cumnoofinv1,"sales":cumsales1,"salesmtd":cumsalesmtd1,"gross":cumgrossavg1,"grossmtd":grossprfmtd1,"noofinv2":cumnoofinv2,"sales2":cumsales2,"salesmtd2":cumsalesmtd2,"gross2":cumgrossavg2,"grossmtd2":grossprfmtd2})
            #data5.append({"date":salesdate,"day":salesdayinwords,"noofinv":cumnoofinv1,"sales":cumsales1,"salesmtd":cumsalesmtd1,"gross":dategrossprfamt,"grossmtd":grossprfmtd1,"noofinv2":cumnoofinv2,"sales2":cumsales2,"salesmtd2":cumsalesmtd2,"gross2":dategrossprfamt2,"grossmtd2":grossprfmtd2})
            if ((cumnoofinv1 > 0)) :
                for i in range(cclength):
                    cstdict["noofinvcstcnt" + str(i)] = cumnoofinv3[i]
                    cstdict["salescstcnt" + str(i)] = cumsales3[i]
                    cstdict["salesmtdcstcnt" + str(i)] = cumsalesmtd3[i]
                    cstdict["grosscstcnt" + str(i)] = cumgrossavg3[i]
                    try:
                        grossprfmtd3[i] = (grossprfmtdcum3[i]/cumsalesmtd3[i])*100
                    except ZeroDivisionError:
                        grossprfmtd3[i] = grossprfmtd3[i]
                        
                    if (cumgrossavg3[i]!=0.0) :
                        cumgrossprfmtd3[i] += cumgrossavg3[i]
                        daysoftxns3[i] += 1

                        #grossprfmtd3[i] = (grossprfmtdcum3[i]/cumsalesmtd3[i])*100
                        #grossprfmtd3[i] = cumgrossprfmtd3[i]/daysoftxns3[i]
                    cstdict["grossmtdcstcnt" + str(i)] = grossprfmtd3[i]

                    #cstdict["noofinvcstcntprv" + str(i)] = cumnoofinv4[i]
                    #cstdict["salescstcntprv" + str(i)] = cumsales4[i]
                    #cstdict["salesmtdcstcntprv" + str(i)] = cumsalesmtd4[i]
                    #cstdict["grosscstcntprv" + str(i)] = cumgrossavg4[i]
                data6.append(cstdict)    
                
    datall=[data5,data6,cstcnt]
    print(lstdata)
    #return data5 
    return datall 


def get_columns(filters):
    long_month_name = filters.get("month")
    curyr = filters.get("year")
    prevyr = int(curyr) - 1
    datetime_object = datetime.datetime.strptime(long_month_name, "%B")
    month_short = datetime_object.strftime("%b")
    columns = [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 90},
        {"label": _("Day"), "fieldname": "day", "fieldtype": "String", "width": 90},
        {
            "label": _("# of Invoices"),
            "fieldname": "noofinv",
            "fieldtype": "Integer",
            "width": 80,
            "convertible": "qty",
        },
        {
            "label": _("Sales"),
            "fieldname": "sales",
            "fieldtype": "Currency",
            "options": "Company:company:default_currency",
            "convertible": "rate",
            "width": 160,
        },
        {
            "label": _("Sales MTD"),
            "fieldname": "salesmtd",
            "fieldtype": "Currency",
            "options": "Company:company:default_currency",
            "width": 160,
        },
        {
            "label": _("Gross %"),
            "fieldname": "gross",
            "fieldtype": "Float",
            "convertible": "qty",
            "width": 90,
        },
        {
            "label": _("Gross % MTD"),
            "fieldname": "grossmtd",
            "fieldtype": "Float",
            "convertible": "qty",
            "width": 90,
        },
        {
            "label": _("# of Invoices(" + month_short + ", " + str(prevyr) + ")"),
            "fieldname": "noofinv2",
            "fieldtype": "Integer",
            "width": 80,
            "convertible": "qty",
        },
        {
            "label": _("Sales( " + month_short + ", " + str(prevyr) + ")"),
            "fieldname": "sales2",
            "fieldtype": "Currency",
            "options": "Company:company:default_currency",
            "convertible": "rate",
            "width": 160,
        },
        {
            "label": _("Sales MTD( "+ month_short + ", " + str(prevyr) + ")"),
            "fieldname": "salesmtd2",
            "fieldtype": "Currency",
            "options": "Company:company:default_currency",
            "convertible": "rate",
            "width": 160,
        },
        {
            "label": _("Gross % (" + month_short + ", " + str(prevyr) + ")"),
            "fieldname": "gross2",
            "fieldtype": "Float",
            "convertible": "qty",
            "width": 90,
        },
        {
            "label": _("Gross % (" + month_short + ", " + str(prevyr) + ")"),
            "fieldname": "grossmtd2",
            "fieldtype": "Float",
            "convertible": "qty",
            "width": 90,
        },
    ]

    return columns	

   


class GrossProfitGenerator(object):
    def __init__(self, filters=None):
        self.data = []
        self.average_buying_rate = {}
        self.filters = frappe._dict(filters)
        self.load_invoice_items()

        self.group_items_by_invoice()

        self.load_stock_ledger_entries()
        self.load_product_bundle()
        self.load_non_stock_items()
        self.get_returned_invoice_items()
        self.process()

    def process(self):
        self.grouped = {}
        self.grouped_data = []

        self.currency_precision = cint(frappe.db.get_default("currency_precision")) or 3
        self.float_precision = cint(frappe.db.get_default("float_precision")) or 2
        self.filters.group_by = "Invoice"
        grouped_by_invoice = True if self.filters.get("group_by") == "Invoice" else False

        buying_amount = 0

        for row in reversed(self.si_list):
            if self.skip_row(row):
                continue

            row.base_amount = flt(row.base_net_amount, self.currency_precision)

            product_bundles = []
            if row.update_stock:
                product_bundles = self.product_bundles.get(row.parenttype, {}).get(row.parent, frappe._dict())
            elif row.dn_detail:
                product_bundles = self.product_bundles.get("Delivery Note", {}).get(
                    row.delivery_note, frappe._dict()
                )
                row.item_row = row.dn_detail

            # get buying amount
            if row.item_code in product_bundles:
                row.buying_amount = flt(
                    self.get_buying_amount_from_product_bundle(row, product_bundles[row.item_code]),
                    self.currency_precision,
                )
            else:
                row.buying_amount = flt(self.get_buying_amount(row, row.item_code), self.currency_precision)

            if grouped_by_invoice:
                if row.indent == 1.0:
                    buying_amount += row.buying_amount
                elif row.indent == 0.0:
                    row.buying_amount = buying_amount
                    buying_amount = 0

            # get buying rate
            if flt(row.qty):
                row.buying_rate = flt(row.buying_amount / flt(row.qty), self.float_precision)
                row.base_rate = flt(row.base_amount / flt(row.qty), self.float_precision)
            else:
                if self.is_not_invoice_row(row):
                    row.buying_rate, row.base_rate = 0.0, 0.0

            # calculate gross profit
            row.gross_profit = flt(row.base_amount - row.buying_amount, self.currency_precision)
            if row.base_amount:
                row.gross_profit_percent = flt(
                    (row.gross_profit / row.base_amount) * 100.0, self.currency_precision
                )
            else:
                row.gross_profit_percent = 0.0

            # add to grouped
            self.grouped.setdefault(row.get(scrub(self.filters.group_by)), []).append(row)

        if self.grouped:
            self.get_average_rate_based_on_group_by()
        #print(self.si_list)    

    def get_average_rate_based_on_group_by(self):
        for key in list(self.grouped):
            if self.filters.get("group_by") != "Invoice":
                for i, row in enumerate(self.grouped[key]):
                    if i == 0:
                        new_row = row
                    else:
                        new_row.qty += flt(row.qty)
                        new_row.buying_amount += flt(row.buying_amount, self.currency_precision)
                        new_row.base_amount += flt(row.base_amount, self.currency_precision)
                new_row = self.set_average_rate(new_row)
                self.grouped_data.append(new_row)
            else:
                for i, row in enumerate(self.grouped[key]):
                    if row.indent == 1.0:
                        if (
                            row.parent in self.returned_invoices and row.item_code in self.returned_invoices[row.parent]
                        ):
                            returned_item_rows = self.returned_invoices[row.parent][row.item_code]
                            for returned_item_row in returned_item_rows:
                                row.qty += flt(returned_item_row.qty)
                                row.base_amount += flt(returned_item_row.base_amount, self.currency_precision)
                            row.buying_amount = flt(flt(row.qty) * flt(row.buying_rate), self.currency_precision)
                        if flt(row.qty) or row.base_amount:
                            row = self.set_average_rate(row)
                            self.grouped_data.append(row)

    def is_not_invoice_row(self, row):
        return (self.filters.get("group_by") == "Invoice" and row.indent != 0.0) or self.filters.get(
            "group_by"
        ) != "Invoice"

    def set_average_rate(self, new_row):
        self.set_average_gross_profit(new_row)
        new_row.buying_rate = (
            flt(new_row.buying_amount / new_row.qty, self.float_precision) if new_row.qty else 0
        )
        new_row.base_rate = (
            flt(new_row.base_amount / new_row.qty, self.float_precision) if new_row.qty else 0
        )
        return new_row

    def set_average_gross_profit(self, new_row):
        new_row.gross_profit = flt(new_row.base_amount - new_row.buying_amount, self.currency_precision)
        new_row.gross_profit_percent = (
            flt(((new_row.gross_profit / new_row.base_amount) * 100.0), self.currency_precision)
            if new_row.base_amount
            else 0
        )
        new_row.buying_rate = (
            flt(new_row.buying_amount / flt(new_row.qty), self.float_precision) if flt(new_row.qty) else 0
        )
        new_row.base_rate = (
            flt(new_row.base_amount / flt(new_row.qty), self.float_precision) if flt(new_row.qty) else 0
        )

    def get_returned_invoice_items(self):
        returned_invoices = frappe.db.sql(
            """
            select
                si.name, si_item.item_code, si_item.stock_qty as qty, si_item.base_net_amount as base_amount, si.return_against
            from
                `tabSales Invoice` si, `tabSales Invoice Item` si_item
            where
                si.name = si_item.parent
                and si.docstatus = 1
                and si.is_return = 1
        """,
            as_dict=1,
        )

        self.returned_invoices = frappe._dict()
        for inv in returned_invoices:
            self.returned_invoices.setdefault(inv.return_against, frappe._dict()).setdefault(
                inv.item_code, []
            ).append(inv)

    def skip_row(self, row):
        if self.filters.get("group_by") != "Invoice":
            if not row.get(scrub(self.filters.get("group_by", ""))):
                return True

        return False

    def get_buying_amount_from_product_bundle(self, row, product_bundle):
        buying_amount = 0.0
        for packed_item in product_bundle:
            if packed_item.get("parent_detail_docname") == row.item_row:
                buying_amount += self.get_buying_amount(row, packed_item.item_code)

        return flt(buying_amount, self.currency_precision)

    def get_buying_amount(self, row, item_code):
        # IMP NOTE
        # stock_ledger_entries should already be filtered by item_code and warehouse and
        # sorted by posting_date desc, posting_time desc
        if item_code in self.non_stock_items and (row.project or row.cost_center):
            # Issue 6089-Get last purchasing rate for non-stock item
            item_rate = self.get_last_purchase_rate(item_code, row)
            return flt(row.qty) * item_rate

        else:
            my_sle = self.sle.get((item_code, row.warehouse))
            if (row.update_stock or row.dn_detail) and my_sle:
                parenttype, parent = row.parenttype, row.parent
                if row.dn_detail:
                    parenttype, parent = "Delivery Note", row.delivery_note

                for i, sle in enumerate(my_sle):
                    # find the stock valution rate from stock ledger entry
                    if (
                        sle.voucher_type == parenttype
                        and parent == sle.voucher_no
                        and sle.voucher_detail_no == row.item_row
                    ):
                        previous_stock_value = len(my_sle) > i + 1 and flt(my_sle[i + 1].stock_value) or 0.0

                        if previous_stock_value:
                            return (previous_stock_value - flt(sle.stock_value)) * flt(row.qty) / abs(flt(sle.qty))
                        else:
                            return flt(row.qty) * self.get_average_buying_rate(row, item_code)
            else:
                return flt(row.qty) * self.get_average_buying_rate(row, item_code)

        return 0.0

    def get_average_buying_rate(self, row, item_code):
        args = row
        if not item_code in self.average_buying_rate:
            args.update(
                {
                    "voucher_type": row.parenttype,
                    "voucher_no": row.parent,
                    "allow_zero_valuation": True,
                    "company": self.filters.company,
                }
            )

            average_buying_rate = get_incoming_rate(args)
            self.average_buying_rate[item_code] = flt(average_buying_rate)

        return self.average_buying_rate[item_code]

    def get_last_purchase_rate(self, item_code, row):
        purchase_invoice = frappe.qb.DocType("Purchase Invoice")
        purchase_invoice_item = frappe.qb.DocType("Purchase Invoice Item")

        query = (
            frappe.qb.from_(purchase_invoice_item)
            .inner_join(purchase_invoice)
            .on(purchase_invoice.name == purchase_invoice_item.parent)
            .select(purchase_invoice_item.base_rate / purchase_invoice_item.conversion_factor)
            .where(purchase_invoice.docstatus == 1)
            .where(purchase_invoice.posting_date <= self.filters.to_date)
            .where(purchase_invoice_item.item_code == item_code)
        )

        if row.project:
            query.where(purchase_invoice_item.project == row.project)

        if row.cost_center:
            query.where(purchase_invoice_item.cost_center == row.cost_center)

        query.orderby(purchase_invoice.posting_date, order=frappe.qb.desc)
        query.limit(1)
        last_purchase_rate = query.run()

        return flt(last_purchase_rate[0][0]) if last_purchase_rate else 0

    def load_invoice_items(self):
        conditions = ""
        if self.filters.company:
            conditions += " and company = %(company)s"
        if self.filters.get("cost_center"):
            conditions += " and `tabSales Invoice Item`.cost_center IN %(cost_center)s"    
        if self.filters.month:
            long_month_name = self.filters.get("month")
            datetime_object = datetime.datetime.strptime(long_month_name, "%B")
            month_number = datetime_object.month
            #conditions += " and MONTH(posting_date) = " + str(month_number)
            conditions += " and ((MONTH(posting_date) = " + str(month_number) + " and YEAR(posting_date) = " + str(self.filters.get("year")) + ")"
            conditions += " or (MONTH(posting_date) = " + str(month_number) + " and YEAR(posting_date) = " + str(int(self.filters.get("year"))-1) + "))"
            #conditions += " and DAY(posting_date) = 3 "
        #if self.filters.year:
            #conditions += " and YEAR(posting_date) = " + str(self.filters.get("year"))
            #conditions += " and posting_date <= %(to_date)s"

        #if self.filters.group_by == "Sales Person":
        #	sales_person_cols = ", sales.sales_person, sales.allocated_amount, sales.incentives"
        #	sales_team_table = "left join `tabSales Team` sales on sales.parent = `tabSales Invoice`.name"
        #else:
        #	sales_person_cols = ""
        #	sales_team_table = ""

        #if self.filters.get("sales_invoice"):
        #	conditions += " and `tabSales Invoice`.name = %(sales_invoice)s"

        #if self.filters.get("item_code"):
        #	conditions += " and `tabSales Invoice Item`.item_code = %(item_code)s"

        self.si_list = frappe.db.sql(
            """
            select
                `tabSales Invoice Item`.parenttype, `tabSales Invoice Item`.parent,
                `tabSales Invoice`.posting_date, `tabSales Invoice`.posting_time,
                `tabSales Invoice`.project, `tabSales Invoice`.update_stock,
                `tabSales Invoice`.customer, `tabSales Invoice`.customer_group,
                `tabSales Invoice`.territory, `tabSales Invoice Item`.item_code,
                `tabSales Invoice Item`.item_name, `tabSales Invoice Item`.description,
                `tabSales Invoice Item`.warehouse, `tabSales Invoice Item`.item_group,
                `tabSales Invoice Item`.brand, `tabSales Invoice Item`.dn_detail,
                `tabSales Invoice Item`.delivery_note, `tabSales Invoice Item`.stock_qty as qty,
                `tabSales Invoice Item`.base_net_rate, `tabSales Invoice Item`.base_net_amount,
                `tabSales Invoice Item`.name as "item_row", `tabSales Invoice`.is_return,
                `tabSales Invoice Item`.cost_center
            
            from
                `tabSales Invoice` inner join `tabSales Invoice Item`
                    on `tabSales Invoice Item`.parent = `tabSales Invoice`.name
                
            where
                `tabSales Invoice`.docstatus=1 and `tabSales Invoice`.is_opening!='Yes' {conditions} {match_cond}
            order by
                `tabSales Invoice`.posting_date desc, `tabSales Invoice`.posting_time desc""".format(
                conditions=conditions,
                match_cond=get_match_cond("Sales Invoice"),
            ),
            self.filters,
            as_dict=1,
        )

    def group_items_by_invoice(self):
        """
        Turns list of Sales Invoice Items to a tree of Sales Invoices with their Items as children.
        """

        parents = []

        for row in self.si_list:
            if row.parent not in parents:
                parents.append(row.parent)

        parents_index = 0
        for index, row in enumerate(self.si_list):
            if parents_index < len(parents) and row.parent == parents[parents_index]:
                invoice = self.get_invoice_row(row)
                self.si_list.insert(index, invoice)
                parents_index += 1

            else:
                # skipping the bundle items rows
                if not row.indent:
                    row.indent = 1.0
                    row.parent_invoice = row.parent
                    row.invoice_or_item = row.item_code

                    if frappe.db.exists("Product Bundle", row.item_code):
                        self.add_bundle_items(row, index)

    def get_invoice_row(self, row):
        return frappe._dict(
            {
                "parent_invoice": "",
                "indent": 0.0,
                "invoice_or_item": row.parent,
                "parent": None,
                "posting_date": row.posting_date,
                "posting_time": row.posting_time,
                "project": row.project,
                "update_stock": row.update_stock,
                "customer": row.customer,
                "customer_group": row.customer_group,
                "item_code": None,
                "item_name": None,
                "description": None,
                "warehouse": None,
                "item_group": None,
                "brand": None,
                "dn_detail": None,
                "delivery_note": None,
                "qty": None,
                "item_row": None,
                "is_return": row.is_return,
                "cost_center": row.cost_center,
                "base_net_amount": frappe.db.get_value("Sales Invoice", row.parent, "base_net_total"),
            }
        )

    def add_bundle_items(self, product_bundle, index):
        bundle_items = self.get_bundle_items(product_bundle)

        for i, item in enumerate(bundle_items):
            bundle_item = self.get_bundle_item_row(product_bundle, item)
            self.si_list.insert((index + i + 1), bundle_item)

    def get_bundle_items(self, product_bundle):
        return frappe.get_all(
            "Product Bundle Item", filters={"parent": product_bundle.item_code}, fields=["item_code", "qty"]
        )

    def get_bundle_item_row(self, product_bundle, item):
        item_name, description, item_group, brand = self.get_bundle_item_details(item.item_code)

        return frappe._dict(
            {
                "parent_invoice": product_bundle.item_code,
                "indent": product_bundle.indent + 1,
                "parent": None,
                "invoice_or_item": item.item_code,
                "posting_date": product_bundle.posting_date,
                "posting_time": product_bundle.posting_time,
                "project": product_bundle.project,
                "customer": product_bundle.customer,
                "customer_group": product_bundle.customer_group,
                "item_code": item.item_code,
                "item_name": item_name,
                "description": description,
                "warehouse": product_bundle.warehouse,
                "item_group": item_group,
                "brand": brand,
                "dn_detail": product_bundle.dn_detail,
                "delivery_note": product_bundle.delivery_note,
                "qty": (flt(product_bundle.qty) * flt(item.qty)),
                "item_row": None,
                "is_return": product_bundle.is_return,
                "cost_center": product_bundle.cost_center,
            }
        )

    def get_bundle_item_details(self, item_code):
        return frappe.db.get_value(
            "Item", item_code, ["item_name", "description", "item_group", "brand"]
        )

    def load_stock_ledger_entries(self):
        res = frappe.db.sql(
            """select item_code, voucher_type, voucher_no,
                voucher_detail_no, stock_value, warehouse, actual_qty as qty
            from `tabStock Ledger Entry`
            where company=%(company)s and is_cancelled = 0
            order by
                item_code desc, warehouse desc, posting_date desc,
                posting_time desc, creation desc""",
            self.filters,
            as_dict=True,
        )
        self.sle = {}
        for r in res:
            if (r.item_code, r.warehouse) not in self.sle:
                self.sle[(r.item_code, r.warehouse)] = []

            self.sle[(r.item_code, r.warehouse)].append(r)

    def load_product_bundle(self):
        self.product_bundles = {}

        for d in frappe.db.sql(
            """select parenttype, parent, parent_item,
            item_code, warehouse, -1*qty as total_qty, parent_detail_docname
            from `tabPacked Item` where docstatus=1""",
            as_dict=True,
        ):
            self.product_bundles.setdefault(d.parenttype, frappe._dict()).setdefault(
                d.parent, frappe._dict()
            ).setdefault(d.parent_item, []).append(d)

    def load_non_stock_items(self):
        self.non_stock_items = frappe.db.sql_list(
            """select name from tabItem
            where is_stock_item=0"""
        )

@frappe.whitelist()
def get_daily_report_record(report_name,filters):	
    # Skipping total row for tree-view reports
    skip_total_row = 0
    #return self.columns, self.data, None, None, skip_total_row
    filterDt= json.loads(filters)	
    filters = frappe._dict(filterDt or {})	
    
        
    if not filters:
        return [], [], None, []

    validate_filters(filters)

    gross_profit_data = GrossProfitGenerator(filters)
    columns = get_columns(filters)
    data = get_merged_dataongrossprofls(filters,gross_profit_data.si_list)
    if not data:
        return [], [], None, []
    
    return columns, data        