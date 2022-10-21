// Copyright (c) 2022, abayomi.awosusi@sgatechsolutions.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Sales Report"] = {
	"filters": [
		{
            fieldname: 'company',
            label: __('Company'),
            fieldtype: 'Link',
            options: 'Company',
            default: frappe.defaults.get_user_default('company')
        },
		{
			"fieldname": "month",
			"fieldtype": "Select",
			"label": "Month",
			"options": [
					 "January",
					 "February",
					 "March",
					 "April",
					 "May",
					 "June",
					 "July",
					 "August",
					 "September",
					 "October",
					 "November",
					 "December"
					 ],
			"default": "",
			"mandatory": 0,
			"wildcard_filter": 0
		   },
		   {
			"fieldname": "year",
			"fieldtype": "Select",
			"label": "Year",
			"options": getyears(),
			"default": new Date().getFullYear(),
			"mandatory": 0,
			"wildcard_filter": 0
		   }
	],
	onload: function(report) {		
		report.page.add_inner_button(__("Export Report"), function() {			
			debugger
			let filters = report.get_values();	
			
			frappe.call({
				method: 'daily_report.daily_report.report.daily_sales_report.daily_sales_report.get_daily_report_record',			
				args: {					
					report_name: report.report_name,
					filters: filters
				},
				callback: function(r) {		
					$(".report-wrapper").html("");					
					$(".justify-center").remove()
					if(r.message[1] != ""){
						dynamic_exportcontent(r.message,filters.company,filters.month,filters.year)		
					}
					else{
						alert("No record found.")
						
					}			
				}
			});				
		});	
		
		
		
	},	
	
};

function dynamic_exportcontent(cnt_list,company,fmonth,fyear){	
	var dynhtml="";
	dynhtml='<div id="dvData">';
	var totlcnt=[];
	var lstCstCntr=[];
	//$.each(cnt_list[0],function(gbl_ind,gbl_val){
	var $crntid="exprtid_1";
	totlcnt[0]="#"+$crntid;
	//lstCstCntr[gbl_ind]=gbl_val[0];
	const Col_list = cnt_list[0];
	//const divcol=Math.ceil(cnt_list[0].length/2); 

	const collist=[];
	//collist[0]=Col_list.slice(1, divcol);
	//collist[1] =Col_list.slice(divcol);

	const titlelist = cnt_list[0]
	const datalist = cnt_list[1][0]
	const datalist2 = cnt_list[1][1]
	const datacostcntlist3 = cnt_list[1][2]

	//console.log(datacostcntlist3)

	dynhtml+='<table style= "font-family: Arial; font-size: 10pt;" id='+$crntid+'>';
	var compnyName="";	
	//compnyName=gbl_ind == 0 ? "Consolidated" : cnt_list[2];
	
	dynhtml+='<caption style="text-align: left;"><span style="font-weight: bold;text-align: left;font-family: Arial; font-size: 10pt;">Sales Statistics For '+company+'</br></span><span style="font-family: Arial; font-size: 10pt; font-weight: normal;text-align: left;">'+ 'Month: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + fmonth + '-' + fyear +'</span><caption>';	
	dynhtml+='<tr><td>&nbsp;</td></tr>';

    dynhtml+='<tr>';
	dynhtml+='<th style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-style: italic;font-family: Arial; font-size: 10pt;" colspan="6"> ' + "&nbsp;" + fmonth + ' ' + fyear + '</span></th>';
    dynhtml+='<th style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-style: italic;font-family: Arial; font-size: 10pt;" colspan="4"> '+ "&nbsp;" + fmonth + ' ' + (parseInt(fyear) - 1).toString()+'</th>';
	//dynhtml+='<td style="text-align: center;border: 1px solid #89898d;font-weight: bold;"><span style="color:white;">"</span>'+fmonth + ' ' + fyear+'<span style="color:white;">"</span></td>';
	//dynhtml+='<td style="text-align: center;border: 1px solid #89898d;font-weight: bold;"><span style="color:white;">"</span>'+fmonth + ' ' + (parseInt(fyear) - 1).toString() +'<span style="color:white;">"</span></td>';
	dynhtml+='</tr>';

	dynhtml+='<tr>';
	for(var cnt=0; cnt < titlelist.length; cnt++) 
	{					
		var colmnth= titlelist[cnt].label.toString();
		var colfldname = titlelist[cnt].fieldname.toString();
		if (colfldname=='noofinv2') {
			colmnth= "# of Inv.'s"
			dynhtml+='<td width="110" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='sales2') {
			colmnth= 'Sales'
			dynhtml+='<td width="150" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='salesmtd2') {
			colmnth= 'Sales MTD'
			dynhtml+='<td width="150" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='gross2') {
			colmnth= 'Gross %'
			dynhtml+='<td width="100" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='sales') {
			dynhtml+='<td width="150" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='salesmtd') {
			dynhtml+='<td width="150" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='noofinv') {
			colmnth= "# of Inv.'s"
			dynhtml+='<td width="110" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='gross') {
			dynhtml+='<td width="100" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='date') {
			dynhtml+='<td width="110" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;font-style: italic;">'+(colmnth).toString()+'</td>';
		}
		else
		//if (colfldname=='day')
		{
		 dynhtml+='<td width="120" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		} 
	//}		
	
	
	}
	//console.log(dynhtml)
	dynhtml+='</tr>';
	var prevyrsalessum = 0
	var prevyrgross = 0
	var noofsalesday = 0
	for(var cnt=0; cnt < datalist.length; cnt++) 
	{					
		
		//rows
		dynhtml+='<tr>';
		dynhtml += (row_celldynFunc(datalist[cnt]))		
		dynhtml+='</tr>';

        prevyrsalessum+= datalist[cnt].sales2
		prevyrgross+= datalist[cnt].gross2
		if (datalist[cnt].gross2!=0) 
		{
		noofsalesday += 1
		}
       		
	}
	let dollarCAD = Intl.NumberFormat("en-CA", {
		style: "currency",
		currency: "CAD",
		useGrouping: true,
	});
	var grossmar = formatAsPercent(prevyrgross/noofsalesday)
	dynhtml+='<tr><td style=""></td><td style=""></td><td style=""></td><td style=""></td><td style=""></td><td style="border-right: 1px solid #89898d;"></td><td style=""></td><td style=""></td><td style=""></td><td style="border-right: 1px solid #89898d;"></td></tr>';
	dynhtml+='<tr><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;border-right: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;border-right: 1px solid #89898d;"></td> </tr>';
	dynhtml+='<tr></tr>';
	dynhtml+='<tr></tr>';
	dynhtml+='<tr></tr>';
	dynhtml+='<tr></tr>';

	dynhtml+='<tr>';
	dynhtml+='<td style="text-align: left;border: 0px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;" colspan="3"> ' + "&nbsp;" + 'Last Year Actual Sales   ' + '</td>';
    dynhtml+='<td style="text-align: right;border: 0px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;" colspan="1"> ' + "&nbsp;" + dollarCAD.format(prevyrsalessum) +  '</td>';
    dynhtml+='</tr>';
	dynhtml+='<tr>';
	dynhtml+='<td style="text-align: left;border: 0px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;" colspan="3"> ' + "&nbsp;" + 'Last Year Actual Margin  ' + '</td>';
    dynhtml+='<td style="text-align: right;border: 0px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;" colspan="1"> ' + "&nbsp;" + grossmar +  '</td>';
	dynhtml+='</tr>';


	dynhtml+='</table>';

	dynhtml+='</div>';
	//console.log(dynhtml)
	//})
	//build second sheet data here
	var $crntid2="exprtid_2";
	totlcnt[1]="#"+$crntid2;

	dynhtml+='<table style= "font-family: Arial; font-size: 10pt;" id='+$crntid2+'>';
	var compnyName="";	
	
	dynhtml+='<caption style="text-align: left;"><span style="font-weight: bold;text-align: left;font-family: Arial; font-size: 10pt;">Sales Statistics For '+company+' by Cost Center</br></span><span style="font-family: Arial; font-size: 10pt; font-weight: normal;text-align: left;">'+ 'Month: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + fmonth + '-' + fyear +'</span><caption>';	
	dynhtml+='<tr><td>&nbsp;</td></tr>';

	dynhtml+='<tr>';
	dynhtml+='<th style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-style: italic;font-family: Arial; font-size: 10pt;" colspan="2"> ' + "&nbsp;Cost Center : " + '</span></th>';
	for(var cnt=0; cnt < datacostcntlist3.length; cnt++) 
	{					
	  var costcntcoltitle= datacostcntlist3[cnt];
	  dynhtml+='<th style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-style: italic;font-family: Arial; font-size: 10pt;" colspan="4"> ' + "&nbsp;" + costcntcoltitle + '</span></th>';
	  //dynhtml+='<th style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-style: italic;font-family: Arial; font-size: 10pt;" colspan="8"> ' + "&nbsp;" + costcntcoltitle + '</span></th>';
	}
	dynhtml+='</tr>';

    dynhtml+='<tr>';
	dynhtml+='<th style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-style: italic;font-family: Arial; font-size: 10pt;" colspan="2"> ' + "&nbsp;" + '</span></th>';
	for(var cnt=0; cnt < datacostcntlist3.length; cnt++) 
	{
	 dynhtml+='<th style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-style: italic;font-family: Arial; font-size: 10pt;" colspan="4"> ' + "&nbsp;" + fmonth + ' ' + fyear + '</span></th>';
     //dynhtml+='<th style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-style: italic;font-family: Arial; font-size: 10pt;" colspan="4"> '+ "&nbsp;" + fmonth + ' ' + (parseInt(fyear) - 1).toString()+'</th>';
	}
	dynhtml+='</tr>';

	dynhtml+='<tr>';
	dynhtml+='<td width="110" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;font-style: italic;">Date</td>';
	dynhtml+='<td width="120" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">Day</td>';
	for(var cnt0=0; cnt0 < datacostcntlist3.length; cnt0++) 
	{
	 for(var cnt=2; cnt < titlelist.length; cnt++) 
	 {					
	    var colmnth= titlelist[cnt].label.toString();
		var colfldname = titlelist[cnt].fieldname.toString();
		/*
		if (colfldname=='noofinv2') {
			colmnth= "# of Inv.'s"
			dynhtml+='<td width="110" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='sales2') {
			colmnth= 'Sales'
			dynhtml+='<td width="150" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='salesmtd2') {
			colmnth= 'Sales MTD'
			dynhtml+='<td width="150" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='gross2') {
			colmnth= 'Gross %'
			dynhtml+='<td width="100" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		*/
		if (colfldname=='sales') {
			dynhtml+='<td width="150" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='salesmtd') {
			dynhtml+='<td width="150" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='noofinv') {
			colmnth= "# of Inv.'s"
			dynhtml+='<td width="110" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='gross') {
			dynhtml+='<td width="100" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='date') {
			dynhtml+='<td width="110" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;font-style: italic;">'+(colmnth).toString()+'</td>';
		}
		else
		if (colfldname=='day') {
			 dynhtml+='<td width="120" style="text-align: center;border: 1px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;">'+(colmnth).toString()+'</td>';
		} 
	  }		
	}

	//console.log(dynhtml)
	dynhtml+='</tr>';
	var prevyrsalessum = 0
	var prevyrgross = 0
	var noofsalesday = 0
	/*
	
	var prevyrsalessum2 = []
	var prevyrgross2 = []
	var noofsalesday2 = []
	for(var cnt2=0; cnt2 < datacostcntlist3.length; cnt2++) 
	{
		prevyrsalessum2[cnt2] = 0.0
	    prevyrgross2[cnt2] = 0.0
	    noofsalesday2[cnt2] = 0.0
	}
	*/		
	var prevcstcnt = ""
	var cstcntkt = 0
	for(var cnt=0; cnt < datalist2.length; cnt++) 
	{					
		
		dynhtml+='<tr>';
		dynhtml += (row_celldynFunc2(datalist2[cnt],datacostcntlist3))		
		dynhtml+='</tr>';

        /*
		for(var cnt2=0; cnt2 < datacostcntlist3.length; cnt2++) 
	    {
			prevyrsalessum2[cnt2]+= datalist2[cnt]["salescstcntprv"+cnt2]
			prevyrgross2[cnt2]+= datalist2[cnt]["grosscstcntprv"+cnt2]
			if (datalist2[cnt]["grosscstcntprv"+cnt2]!=0) 
		    {
		      noofsalesday2[cnt2] += 1
		    }
		}
		*/	
	}

	let dollarCAD2 = Intl.NumberFormat("en-CA", {
		style: "currency",
		currency: "CAD",
		useGrouping: true,
	});
    var grossmar2 = []

	dynhtml+='<tr>'
	dynhtml+='<td style=""></td><td style="">'
	for(var cnt=0; cnt < datacostcntlist3.length; cnt++) 
	{
	    dynhtml+='<td style=""></td><td style=""></td><td style=""></td><td style="border-right: 1px solid #89898d;"></td>';
		//dynhtml+='<td style=""></td><td style=""></td><td style=""></td><td style="border-right: 1px solid #89898d;"></td><td style=""></td><td style=""></td><td style=""></td><td style="border-right: 1px solid #89898d;"></td>';
	}
	dynhtml+='</tr>'
	dynhtml+='<tr>'
	dynhtml+='<td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td>'
	for(var cnt=0; cnt < datacostcntlist3.length; cnt++) 
	{
		dynhtml+='<td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;border-right: 1px solid #89898d;"></td>'
	 //dynhtml+='<td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;border-right: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;"></td><td style="border-bottom: 1px solid #89898d;border-right: 1px solid #89898d;"></td>'
	}
	dynhtml+='</tr>'
	dynhtml+='<tr></tr>';
	dynhtml+='<tr></tr>';
	dynhtml+='<tr></tr>';
	dynhtml+='<tr></tr>';
    /*
	for(var cnt=0; cnt < datacostcntlist3.length; cnt++) 
	{
	 grossmar2[cnt] = formatAsPercent(prevyrgross2[cnt]/noofsalesday2[cnt])
	dynhtml+='<tr>';
	dynhtml+='<td style="text-align: left;border: 0px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;" colspan="7"> ' + "&nbsp;" + 'Last Year Actual Sales - ' + datacostcntlist3[cnt]  + '</td>';
    dynhtml+='<td style="text-align: right;border: 0px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;" colspan="1"> ' + "&nbsp;" + dollarCAD.format(prevyrsalessum2[cnt]) +  '</td>';
    dynhtml+='</tr>';
	dynhtml+='<tr>';
	dynhtml+='<td style="text-align: left;border: 0px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;" colspan="7"> ' + "&nbsp;" + 'Last Year Actual Margin - ' + datacostcntlist3[cnt]  + '</td>';
    dynhtml+='<td style="text-align: right;border: 0px solid #89898d;font-weight: bold;font-family: Arial; font-size: 10pt;" colspan="1"> ' + "&nbsp;" + grossmar2[cnt] +  '</td>';
	dynhtml+='</tr>';
	}
    */ 
	dynhtml+='</table>';

	dynhtml+='</div>';

	$(".report-wrapper").hide();
	$(".report-wrapper").append(dynhtml);	
	//tablesToExcel(totlcnt, lstCstCntr,'SalesDailyReport.xls')

	




	tablesToExcel(totlcnt, 'SalesDailyReport.xls')
}

function row_celldynFunc(colDt){	
	const options = { year: 'numeric', month: 'short', day: 'numeric' }
	//const new Date(date).toLocaleDateString('en-CA', options)
	let dollarCAD = Intl.NumberFormat("en-CA", {
		style: "currency",
		currency: "CAD",
		useGrouping: true,
	});
	let amountFormatter = Intl.NumberFormat("en-CA", {
		style: "decimal",
		useGrouping: true,
		minimumFractionDigits: 2,
	    maximumFractionDigits: 2,
	});
	celldynhtml="";
	celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+new Date(colDt.date).toLocaleDateString('en-CA', options)+'</td>';
    celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+colDt.day+'</td>';
	celldynhtml+='<td style="text-align: center;font-family: Arial; font-size: 10pt;">'+colDt.noofinv+'</td>';
	celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+amountFormatter.format(colDt.sales)+'</td>';
	celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+dollarCAD.format(colDt.salesmtd)+'</td>';
	celldynhtml+='<td style="font-family: Arial; font-size: 10pt; border-right: 1px solid #89898d;">'+formatAsPercent(colDt.gross)+'</td>';
	celldynhtml+='<td style="font-family: Arial; font-size: 10pt; text-align: center;">'+colDt.noofinv2+'</td>';
	celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+amountFormatter.format(colDt.sales2)+'</td>';
	celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+dollarCAD.format(colDt.salesmtd2)+'</td>';
	celldynhtml+='<td style="font-family: Arial; font-size: 10pt; border-right: 1px solid #89898d;">'+formatAsPercent(colDt.gross2)+'</td>';
    
	return celldynhtml;
}


function row_celldynFunc2(colDt, costcentlst){	
	const options = { year: 'numeric', month: 'short', day: 'numeric' }
	//const new Date(date).toLocaleDateString('en-CA', options)
	let dollarCAD = Intl.NumberFormat("en-CA", {
		style: "currency",
		currency: "CAD",
		useGrouping: true,
	});
	let amountFormatter = Intl.NumberFormat("en-CA", {
		style: "decimal",
		useGrouping: true,
		minimumFractionDigits: 2,
	    maximumFractionDigits: 2,
	});
	celldynhtml="";
	celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+new Date(colDt.date).toLocaleDateString('en-CA', options)+'</td>';
    celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+colDt.day+'</td>';
    for(var cnt=0; cnt < costcentlst.length; cnt++) 
	{
		var col1 = 'noofinvcstcnt' + cnt
		var col2 = 'salescstcnt' + cnt
		var col3 = 'salesmtdcstcnt' + cnt
		var col4 = 'grosscstcnt' + cnt
		//var col5 = 'noofinvcstcntprv' + cnt
		//var col6 = 'salescstcntprv' + cnt
		//var col7 = 'salesmtdcstcntprv' + cnt
		//var col8 = 'grosscstcntprv' + cnt
		
	    celldynhtml+='<td style="text-align: center;font-family: Arial; font-size: 10pt;">'+colDt[col1]+'</td>';
	    celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+amountFormatter.format(colDt[col2])+'</td>';
	    celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+dollarCAD.format(colDt[col3])+'</td>';
	    celldynhtml+='<td style="font-family: Arial; font-size: 10pt; border-right: 1px solid #89898d;">'+formatAsPercent(colDt[col4])+'</td>';
	    //celldynhtml+='<td style="font-family: Arial; font-size: 10pt; text-align: center;">'+colDt[col5]+'</td>';
	    //celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+amountFormatter.format(colDt[col6])+'</td>';
	    //celldynhtml+='<td style="font-family: Arial; font-size: 10pt;">'+dollarCAD.format(colDt[col7])+'</td>';
	    //celldynhtml+='<td style="font-family: Arial; font-size: 10pt; border-right: 1px solid #89898d;">'+formatAsPercent(colDt[col8])+'</td>';
	}
	return celldynhtml;
}


function getyears(){
	let yrarr = [];
	curyr = new Date().getFullYear();
	for (let i = 0; i < 10; i++) {
	   yrarr.push(curyr);
	   curyr = curyr -1;
	 }
	return yrarr;
}

function formatAsPercent(num) {
	return new Intl.NumberFormat('default', {
	  style: 'percent',
	  minimumFractionDigits: 2,
	  maximumFractionDigits: 2,
	}).format(num / 100);
  }

  
/** */


/**/

//for test 
function exportTableToCSV() {
 
	// Variable to store the final csv data
	var csv_data = [];

	// Get each row data
	var rows = $("#dvData").find('tr');//document.getElementsByTagName('tr');
	for (var i = 0; i < rows.length; i++) {

		// Get each column data
		var cols = rows[i].querySelectorAll('td,th');

		// Stores each csv row data
		var csvrow = [];
		for (var j = 0; j < cols.length; j++) {

			// Get the text data of each cell
			// of a row and push it to csvrow
			csvrow.push(cols[j].innerHTML);
		}

		// Combine each column value with comma
		csv_data.push(csvrow.join(","));
	}

	// Combine each row data with new line character
	csv_data = csv_data.join('\n');

	// Call this function to download csv file 
	downloadCSVFile(csv_data);

}

function downloadCSVFile(csv_data) {

	// Create CSV file object and feed
	// our csv_data into it
	CSVFile = new Blob([csv_data], {
		type: "text/csv"
	});

	// Create to temporary link to initiate
	// download process
	var temp_link = document.createElement('a');

	// Download csv file
	temp_link.download = "SalesDailyReport.csv";
	var url = window.URL.createObjectURL(CSVFile);
	temp_link.href = url;

	// This link should not be displayed
	temp_link.style.display = "none";
	document.body.appendChild(temp_link);

	// Automatically click the link to
	// trigger download
	temp_link.click();
	document.body.removeChild(temp_link);
}

var tablesToExcel = (function () {
	var uri = 'data:application/vnd.ms-excel;base64,'
		, html_start = `<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">`
		, template_ExcelWorksheet = `<x:ExcelWorksheet><x:Name>{SheetName}</x:Name><x:WorksheetSource HRef="sheet{SheetIndex}.htm"/></x:ExcelWorksheet>`
		, template_ListWorksheet = `<o:File HRef="sheet{SheetIndex}.htm"/>`
		, template_HTMLWorksheet = `
------=_NextPart_dummy
Content-Location: sheet{SheetIndex}.htm
Content-Type: text/html; charset=windows-1252

` + html_start + `
<head>
<meta http-equiv="Content-Type" content="text/html; charset=windows-1252">
<link id="Main-File" rel="Main-File" href="../WorkBook.htm">
<link rel="File-List" href="filelist.xml">
</head>
<body><table>{SheetContent}</table></body>
</html>`
		, template_WorkBook = `MIME-Version: 1.0
X-Document-Type: Workbook
Content-Type: multipart/related; boundary="----=_NextPart_dummy"

------=_NextPart_dummy
Content-Location: WorkBook.htm
Content-Type: text/html; charset=windows-1252

` + html_start + `
<head>
<meta name="Excel Workbook Frameset">
<meta http-equiv="Content-Type" content="text/html; charset=windows-1252">
<link rel="File-List" href="filelist.xml">
<!--[if gte mso 9]><xml>
<x:ExcelWorkbook>
<x:ExcelWorksheets>{ExcelWorksheets}</x:ExcelWorksheets>
<x:ActiveSheet>0</x:ActiveSheet>
</x:ExcelWorkbook>
</xml><![endif]-->
</head>
<frameset>
<frame src="sheet0.htm" name="frSheet">
<noframes><body><p>This page uses frames, but your browser does not support them.</p></body></noframes>
</frameset>
</html>
{HTMLWorksheets}
Content-Location: filelist.xml
Content-Type: text/xml; charset="utf-8"

<xml xmlns:o="urn:schemas-microsoft-com:office:office">
<o:MainFile HRef="../WorkBook.htm"/>
{ListWorksheets}
<o:File HRef="filelist.xml"/>
</xml>
------=_NextPart_dummy--
`
		, base64 = function (s) { return window.btoa(unescape(encodeURIComponent(s))) }
		, format = function (s, c) { return s.replace(/{(\w+)}/g, function (m, p) { return c[p]; }) }
	return function (tables, filename) {
		var context_WorkBook = {
			ExcelWorksheets: ''
			, HTMLWorksheets: ''
			, ListWorksheets: ''
		};		
		var tables = jQuery(tables);
		var tbk = 0
		//SheetIndex =1;
		$.each(tables, function (SheetIndex,val) {			
			var $table = $(val);
			var SheetName = "";
			if (SheetIndex == 0) {
				SheetName = 'Consolidated Daily Sales' ;
			}
			else if(SheetIndex == 1) {
				SheetName = 'Daily Sales by Cost Center' ;
			}
			context_WorkBook.ExcelWorksheets += format(template_ExcelWorksheet, {
				SheetIndex: SheetIndex
				, SheetName: SheetName
			});
			context_WorkBook.HTMLWorksheets += format(template_HTMLWorksheet, {
				SheetIndex: SheetIndex
				, SheetContent: $table.html()
			});
			context_WorkBook.ListWorksheets += format(template_ListWorksheet, {
				SheetIndex: SheetIndex
			});
			tbk += 1
		});

		var link = document.createElement("A");
		link.href = uri + base64(format(template_WorkBook, context_WorkBook));
		link.download = filename || 'Workbook.xls';
		link.target = '_blank';
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}
})();




