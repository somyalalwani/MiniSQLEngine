import os
import re
import csv
import sqlparse
import itertools
import sys

def metadata_to_dict():
	table_structure={}
	files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt') and f.startswith('metadata')]
	for i in range(len(files)):
		c1=open(files[i])
		s=c1.read()
		#print(s)
		result = re.split("\n<begin_table>\n",s)
		
		cols=result[0].split('\n')
		cols.pop()
		if(len(result)==1):
			cols.pop()
		table_name=cols[1]
		cols_name=cols[2:]
		table_structure[table_name]=cols_name
		#print(table_structure)
		#print("-----")	
		length=len(result)
		j=1
		while j<length-1:
			#print("j=",j)
			col=result[j].split('\n')
			col.pop()
			table_name=col[0]
			cols_name=col[1:]
			table_structure[table_name]=cols_name
			j=j+1

		if(length>1):
			col=result[j].split('\n')
			col.pop()
			col.pop()
			table_name=col[0]
			cols_name=col[1:]
			table_structure[table_name]=cols_name
			
	return table_structure




def csv_to_dict():
	table_data={}
	files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.csv')]
	for file in files:
		filenam=str(file)
		filename=filenam[:-4]
		with open(file, newline='') as fo:
			reader = csv.reader(fo)
			data = list(reader)
			table_data[filename]=data
	#print(table_data['table1'][0])
	#print(table_data['table2'])
	return table_data

def capital(str_list,i):
	length=len(str_list)
	for n in range(i+1,length):
		if str_list[n].isupper():
			return n
		else:
			continue
	return n

def split_list(str_list):
	l=[]
	for i in str_list:
		l+=i.split('=')
	return l

def cartesian_product(r,x):
    ls=[]

    for i in r:
        for j in x:
            temp=[]
            temp.extend(i)
            temp.extend(j)
            
            #print(temp)
            ls.append(temp)
    #print(len(ls))
    #print("--------------------")
    return ls   


table_structure=metadata_to_dict()
#print(table_structure)

table_data = csv_to_dict()
#print(table_data)

query=str(sys.argv[1])

#query="SELECT City FROM citizen, city ON citizencity_id = citycity_id WHERE citcityname != 'San Bruno' GROUP BY citycityname HAVING COUNT(*) >= 2 ORDER BY citycityname"

a=sqlparse.format(query,keyword_case='upper')

#print(a)
#a="SELECT count(*) FROM table1,table2 GROUP BY A;"

if(a.endswith(";")):
	pass
else:
	print("No semicolon at the end, but still processing the query")
	a=a+';'	
print()
print("*******OUTPUT************")
print()
parsed=sqlparse.parse(a)
stmt=parsed[0]
list1=[]
for token in stmt.tokens:
	if(str(token)!=" "):
		list1.append(str(token))
"""
for i in list1:
	print(i)
"""

list=a.split(" ")
list[-1]=(list[-1])[:-1]

#print(list)

index_of_from = list.index('FROM')
i=capital(list,index_of_from)
#print(i)
if(index_of_from+1<i and i<len(list)-1):
	from1_data=list[index_of_from+1:i]
elif(index_of_from+1<i and i==len(list)-1):
	from1_data=list[index_of_from+1:]
elif(type(list[i])==str):
	from1_data=list[i].split(",")
else:
	from1_data=list[i].split(",")

from_data=(' '.join(from1_data)).split(",")

#print(from_data)
#print(table_structure)
final_col_names=[]
from_final_data=[]

try:
	if(len(from_data)>1):
		from_final_data = table_data[from_data[0].replace(',',"").replace("'","").lstrip().rstrip()]
		for i in range(len(from_data)): 
			final_col_names.extend(table_structure[from_data[i].replace(',',"").rstrip().lstrip()])
		for element in range(1,len(from_data)):
			from_final_data=cartesian_product(from_final_data,table_data[from_data[element].rstrip().lstrip().replace("'","")])

	else :
		from_final_data = table_data[from_data[0].replace(',',"").replace("'","")]
		final_col_names.extend(table_structure[from_data[0].replace(',',"").rstrip().lstrip()])
except:
	print("Enter correct table/column name")

#print("final col names:")
#print(final_col_names)
#print(from_final_data)
try:
	index_of_where = list.index('WHERE')
	i=0
	for i in range(len(list1)):
		if(list1[i].startswith("WHERE")):
			break;

	condition1=None
	condition2=None
	where_data=[]
	flag1=None
	flag2=None


	if(i!=len(list1) and list1[i].find("AND")!=-1):
			condition1=list1[i][6:list1[i].find("AND")]
			condition2=list1[i][list1[i].find("AND")+4:]
			
			if "<=" in condition1:
				flag1=1
			elif ">=" in condition1:
				flag1=2
			elif ">" in condition1:
				flag1=3
			elif "<" in condition1:
				flag1=4
			elif "=" in condition1:
				flag1=5

			if "<=" in condition2:
				flag2=1
			elif ">=" in condition2:
				flag2=2
			elif ">" in condition2:
				flag2=3
			elif "<" in condition2:
				flag2=4
			elif "=" in condition2:
				flag2=5
			
			if(flag1==1):
				condition1=condition1.split("<=")
			elif (flag1==2):
				condition1=condition1.split(">=")
			elif(flag1==3):
				condition1=condition1.split(">")
			elif(flag1==4):
				condition1=condition1.split("<")
			else:
				condition1=condition1.split("=")

			if(flag2==1):
				condition2=condition2.split("<=")
			elif (flag2==2):
				condition2=condition2.split(">=")
			elif(flag2==3):
				condition2=condition2.split(">")
			elif(flag2==4):
				condition2=condition2.split("<")
			else:
				condition2=condition2.split("=")
			
			#print(condition1)
			#print(condition2)
			
			condition1[0]=condition1[0].rstrip(";").rstrip(" ").lstrip(" ")
			condition1[1]=condition1[1].rstrip(";").rstrip(" ").lstrip(" ")
			condition2[0]=condition2[0].rstrip(";").rstrip(" ").lstrip(" ")
			condition2[1]=condition2[1].rstrip(";").rstrip(" ").lstrip(" ")
			col1_index=final_col_names.index(condition1[0])
			col2_index=final_col_names.index(condition2[0])
			col1_value=condition1[1]
			col2_value=condition2[1]
			j=0
			# condition2 : from_final_data[j][col2_index]==col2_value
			if(flag1==5):
				while(j<len(from_final_data)):
					if (int(from_final_data[j][col1_index])==int(col1_value)):
						j=j+1
					else:
						from_final_data.pop(j)
					
			elif(flag1==4):
				while(j<len(from_final_data)):
					if (int(from_final_data[j][col1_index])<int(col1_value)):
						j=j+1
					else:
						from_final_data.pop(j)
			elif(flag1==3):
				while(j<len(from_final_data)):
					if (int(from_final_data[j][col1_index])>int(col1_value)):
						j=j+1
					else:
						from_final_data.pop(j)
			elif(flag1==2):
				while(j<len(from_final_data)):
					if (int(from_final_data[j][col1_index])>=int(col1_value)):
						j=j+1
					else:
						from_final_data.pop(j)
			elif(flag1==1):
				while(j<len(from_final_data)):
					if (int(from_final_data[j][col1_index])<=int(col1_value)):
						j=j+1
					else:
						from_final_data.pop(j)
			
			j=0
			
			if(flag2==5):
				while(j<len(from_final_data)):
					if (int(from_final_data[j][col2_index])==int(col2_value)):
						j=j+1
					else:
						from_final_data.pop(j)
					
			elif(flag2==4):
				while(j<len(from_final_data)):
					if (int(from_final_data[j][col2_index])<int(col2_value)):
						j=j+1
					else:
						from_final_data.pop(j)
			elif(flag2==3):
				while(j<len(from_final_data)):
					if (int(from_final_data[j][col2_index])>int(col2_value)):
						j=j+1
					else:
						from_final_data.pop(j)
			elif(flag2==2):
				while(j<len(from_final_data)):
					if (int(from_final_data[j][col2_index])>=int(col2_value)):
						j=j+1
					else:
						from_final_data.pop(j)
			elif(flag2==1):
				while(j<len(from_final_data)):
					if (int(from_final_data[j][col2_index])<=int(col2_value)):
						j=j+1
					else:
						from_final_data.pop(j)
			

	elif(i!=len(list1) and list1[i].find("OR")!=-1):
		condition1=list1[i][6:list1[i].find("OR")]
		condition2=list1[i][list1[i].find("OR")+3:]

		if "<=" in condition1:
			flag1=1
		elif ">=" in condition1:
			flag1=2
		elif ">" in condition1:
			flag1=3
		elif "<" in condition1:
			flag1=4
		elif "=" in condition1:
			flag1=5
		
		if "<=" in condition2:
			flag2=1
		elif ">=" in condition2:
			flag2=2
		elif ">" in condition2:
			flag2=3
		elif "<" in condition2:
			flag2=4
		elif "=" in condition2:
			flag2=5
			
		if(flag1==1):
			condition1=condition1.split("<=")
		elif (flag1==2):
			condition1=condition1.split(">=")
		elif(flag1==3):
			condition1=condition1.split(">")
		elif(flag1==4):
			condition1=condition1.split("<")
		else:
			condition1=condition1.split("=")

		if(flag2==1):
			condition2=condition2.split("<=")
		elif (flag2==2):
			condition2=condition2.split(">=")
		elif(flag2==3):
			condition2=condition2.split(">")
		elif(flag2==4):
			condition2=condition2.split("<")
		else:
			condition2=condition2.split("=")
				
		#print(condition1)
		#print(condition2)
			

		condition1[0]=condition1[0].rstrip(";").rstrip(" ").lstrip(" ")
		condition1[1]=condition1[1].rstrip(";").rstrip(" ").lstrip(" ")
		condition2[0]=condition2[0].rstrip(";").rstrip(" ").lstrip(" ")
		condition2[1]=condition2[1].rstrip(";").rstrip(" ").lstrip(" ")
		col1_index=final_col_names.index(condition1[0])
		col2_index=final_col_names.index(condition2[0])
		col1_value=condition1[1]
		col2_value=condition2[1]
		j=0
		
		if(flag1==1 and flag2==1):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<=int(col1_value) or int(from_final_data[j][col2_index])<=int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==1 and flag2==2):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<=int(col1_value) or int(from_final_data[j][col2_index])>=int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==1 and flag2==3):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<=int(col1_value) or int(from_final_data[j][col2_index])>int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==1 and flag2==4):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<=int(col1_value) or int(from_final_data[j][col2_index])<int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==1 and flag2==5):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<=int(col1_value) or int(from_final_data[j][col2_index])==int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==2 and flag2==1):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<=int(col1_value) or int(from_final_data[j][col2_index])<=int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==2 and flag2==2):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>=int(col1_value) or int(from_final_data[j][col2_index])>=int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==2 and flag2==3):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>=int(col1_value) or int(from_final_data[j][col2_index])>int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==2 and flag2==4):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>=int(col1_value) or int(from_final_data[j][col2_index])<int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==2 and flag2==5):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>=int(col1_value) or int(from_final_data[j][col2_index])==int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==3 and flag2==1):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>int(col1_value) or int(from_final_data[j][col2_index])<=int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==3 and flag2==2):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>int(col1_value) or int(from_final_data[j][col2_index])>=int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==3 and flag2==3):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>int(col1_value) or int(from_final_data[j][col2_index])>int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==3 and flag2==4):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>int(col1_value) or int(from_final_data[j][col2_index])<int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==3 and flag2==5):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>int(col1_value) or int(from_final_data[j][col2_index])==int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==4 and flag2==1):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<int(col1_value) or int(from_final_data[j][col2_index])<=int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==4 and flag2==2):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<int(col1_value) or int(from_final_data[j][col2_index])>=int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==4 and flag2==3):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<int(col1_value) or int(from_final_data[j][col2_index])>int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==4 and flag2==4):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<int(col1_value) or int(from_final_data[j][col2_index])<int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==4 and flag2==5):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<int(col1_value) or int(from_final_data[j][col2_index])==int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==5 and flag2==1):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])==int(col1_value) or int(from_final_data[j][col2_index])<=int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==5 and flag2==2):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<=int(col1_value) or int(from_final_data[j][col2_index])>=int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==5 and flag2==3):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])==int(col1_value) or int(from_final_data[j][col2_index])>int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==5 and flag2==4):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])==int(col1_value) or int(from_final_data[j][col2_index])<int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==5 and flag2==5):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])==int(col1_value) or int(from_final_data[j][col2_index])==int(col2_value)):
					j=j+1
				else:
					from_final_data.pop(j)


	else:
		condition1=list1[i][6:]

		if "<=" in condition1:
			flag1=1
		elif ">=" in condition1:
			flag1=2
		elif ">" in condition1:
			flag1=3
		elif "<" in condition1:
			flag1=4
		elif "=" in condition1:
			flag1=5
			
		if(flag1==1):
			condition1=condition1.split("<=")
		elif (flag1==2):
			condition1=condition1.split(">=")
		elif(flag1==3):
			condition1=condition1.split(">")
		elif(flag1==4):
			condition1=condition1.split("<")
		else:
			condition1=condition1.split("=")

		condition1[0]=condition1[0].rstrip(";").rstrip(" ").lstrip(" ")
		condition1[1]=condition1[1].rstrip(";").rstrip(" ").lstrip(" ")
		col1_index=final_col_names.index(condition1[0])
		col1_value=condition1[1]
		j=0

		if(flag1==5):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])==int(col1_value)):
					j=j+1
				else:
					from_final_data.pop(j)
					
		elif(flag1==4):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<int(col1_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==3):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>int(col1_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==2):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])>=int(col1_value)):
					j=j+1
				else:
					from_final_data.pop(j)
		elif(flag1==1):
			while(j<len(from_final_data)):
				if (int(from_final_data[j][col1_index])<=int(col1_value)):
					j=j+1
				else:
					from_final_data.pop(j)
	"""		
	print("---------------after where ----------")
	print(from_final_data)
	"""
except:
	pass

try:
	index_of_order = list.index('ORDER')
	i=capital(list,index_of_order+1)
	if(i>index_of_order+2):
		order_data=list[index_of_order+2:i]
	else:
		order_data=list[i]
	
	try:
		index_of_orderby_in_columns=final_col_names.index(order_data)
		#print(final_col_names)
		if(i+1==len(list) or list[i+1]=='ASC' or (list[i+1]!="ASC" and list[i+1]!="DESC")):
				#from_final_data.sort(key = lambda Y: Y[index_of_orderby_in_columns])
				#print("ASCCCCC")
				l = len(from_final_data) 
				for q in range(0, l): 
					for r in range(0, l-q-1): 
						if (int(from_final_data[r][index_of_orderby_in_columns]) > int(from_final_data[r + 1][index_of_orderby_in_columns])): 
							tempo = from_final_data[r] 
							from_final_data[r]= from_final_data[r + 1] 
							from_final_data[r + 1]= tempo
					
		elif(list[i+1]=='DESC'):
			#from_final_data.sort(key = lambda Y: Y[index_of_orderby_in_columns],reverse=True)
			#print("DESCCCCCC")
			l = len(from_final_data) 
			for q in range(0, l): 
				for r in range(0, l-q-1): 
					if (int(from_final_data[r][index_of_orderby_in_columns]) < int(from_final_data[r + 1][index_of_orderby_in_columns])): 
						tempo = from_final_data[r] 
						from_final_data[r]= from_final_data[r + 1] 
						from_final_data[r + 1]= tempo
		
	except:
		print("No such column for order by")

except:
	pass

flag_groupby=0

try:
	index_of_group = list.index('GROUP')
	flag_groupby=1
	i=capital(list,index_of_group+1)
	if(i>index_of_group+2):
		group_data=list[index_of_group+2:i]
	else:
		group_data=list[i]

	try:
		index_of_groupby_in_columns=final_col_names.index(group_data)

		if(index_of_groupby_in_columns!=-1):
			d = {}
			for row in from_final_data:
				if row[index_of_groupby_in_columns] not in d:
					d[str(row[index_of_groupby_in_columns])] = []
				d[str(row[index_of_groupby_in_columns])].append(row)
		   # Add all non-Name attributes as a new list
			#print("----AFTER GROUP BY-----")
			#print(d)
		
		else:
			print("query has some problem -  no such group by column name")
	except:
		print("query doesn't exist -  no such group by column name")

	##NOW 'd' has final data
except:
	pass

# select clause :
select_data=str(list1[1])
if(select_data=="DISTINCT"):
	select_data = str(list1[2])

select_data=select_data.split(",")
"""
for i in select_data:
	print(i,end=" ")
"""
length=len(select_data)
i=0

if(flag_groupby!=1 and select_data[0]=="*" and str(list1[1])!="DISTINCT" ):
	select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
	for qq in final_col_names:
		print(qq,end=" ")
	print()
	for x in from_final_data:
		for y in x:
			print(y,end=" ")
		print()
if(flag_groupby!=1 and select_data[0]=="*" and str(list1[1])=="DISTINCT" ):
	select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
	for qq in final_col_names:
		print(qq,end=" ")
	print()
	L=[]
	for x in from_final_data:
		if x not in L:
			L.append(x)
			for y in x:
				print(y,end=" ")
			print()

#try:
if(flag_groupby!=1 and str(list1[1])!="DISTINCT" and (select_data[0].startswith("count") or select_data[0].startswith("max") or select_data[0].startswith("min") or select_data[0].startswith("sum") or select_data[0].startswith("avg"))):
	
	try:
		
		for i in range(length):
			
			select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
			
			if(select_data[i].startswith("max") and flag_groupby!=1):
				i1=str(select_data[i]).index("(")
				i2=str(select_data[i]).index(")")
				column_name=str(select_data[i])[i1+1:i2]
				column_index=final_col_names.index(column_name)
				max=0
				for row in from_final_data:
					if(int(row[column_index])>max):
						max=int(row[column_index])
				print(select_data[i])
				print(max)

			elif(select_data[i].startswith("min") and flag_groupby!=1):
				i1=str(select_data[i]).index("(")
				i2=str(select_data[i]).index(")")
				column_name=str(select_data[i])[i1+1:i2]
				column_index=final_col_names.index(column_name)
				min=0
				for row in from_final_data:
					if(int(row[column_index])<min):
						min=int(row[column_index])
				print(select_data[i])
				print(min)
		
			elif(select_data[i].startswith("count") and flag_groupby!=1):	
				i1=str(select_data[i]).index("(")
				i2=str(select_data[i]).index(")")
				column_name=str(select_data[i])[i1+1:i2]
				if(column_name!="*"):
					count = 0
					for row in from_final_data:
							count+=1
					print(select_data[i])
					print(count)
				else:
					count=0
					for row in from_final_data:
						count+=1
					print(select_data[i])
					print(count)
			elif(select_data[i].startswith("avg") and flag_groupby!=1):
				i1=str(select_data[i]).index("(")
				i2=str(select_data[i]).index(")")
				column_name=str(select_data[i])[i1+1:i2]
				column_index=final_col_names.index(column_name)
				sum=0
				count=0
				for row in from_final_data:
					sum+=int(row[column_index])
					count+=1
				print(select_data[i])
				if(count==0):
					print("Count=0, so no avg")
				else:
					print(float(sum)/float(count))
			
			elif(select_data[i].startswith("sum") and flag_groupby!=1):
				i1=str(select_data[i]).index("(")
				i2=str(select_data[i]).index(")")
				column_name=str(select_data[i])[i1+1:i2]
				column_index=final_col_names.index(column_name)
				sum=0
				for row in from_final_data:
					sum+=int(row[column_index])
				print(select_data[i])
				print(sum)
			else :
				print("Invalid Query with aggregate functions")

	except:
		print("Invalid Query with aggregate functions")

elif(flag_groupby!=1 and str(list1[1])=="DISTINCT" and (select_data[0].startswith("count") or select_data[0].startswith("max") or select_data[0].startswith("min") or select_data[0].startswith("sum") or select_data[0].startswith("avg"))):
	#try:
	for xx in select_data:
		print(xx,end=" ")
	xx=[]
	for i in range(length):
		select_data[i]=select_data[i].rstrip(" ").lstrip(" ")

		if(select_data[i].startswith("max") and flag_groupby!=1):
			i1=str(select_data[i]).index("(")
			i2=str(select_data[i]).index(")")
			column_name=str(select_data[i])[i1+1:i2]
			column_index=final_col_names.index(column_name)
			max=0
			for row in from_final_data:
				if(int(row[column_index])>max):
					max=int(row[column_index])
			xx.append(max)

		elif(select_data[i].startswith("min") and flag_groupby!=1):
			i1=str(select_data[i]).index("(")
			i2=str(select_data[i]).index(")")
			column_name=str(select_data[i])[i1+1:i2]
			column_index=final_col_names.index(column_name)
			min=0
			for row in from_final_data:
				if(int(row[column_index])<min):
					min=int(row[column_index])
			xx.append(min)
	
		elif(select_data[i].startswith("count") and flag_groupby!=1):	
			i1=str(select_data[i]).index("(")
			i2=str(select_data[i]).index(")")
			column_name=str(select_data[i])[i1+1:i2]
			if(column_name!="*"):
				count = 0
				for row in from_final_data:
						count+=1
				xx.append(count)
			else:
				count=0
				for row in from_final_data:
					count+=1
				xx.append(count)
		elif(select_data[i].startswith("avg") and flag_groupby!=1):
			i1=str(select_data[i]).index("(")
			i2=str(select_data[i]).index(")")
			column_name=str(select_data[i])[i1+1:i2]
			column_index=final_col_names.index(column_name)
			sum=0
			count=0
			for row in from_final_data:
				sum+=int(row[column_index])
				count+=1
			if(count==0):
				xx.append("undefined")

			else:
				xx.append(float(sum)/float(count))
		
		elif(select_data[i].startswith("sum") and flag_groupby!=1):
			i1=str(select_data[i]).index("(")
			i2=str(select_data[i]).index(")")
			column_name=str(select_data[i])[i1+1:i2]
			column_index=final_col_names.index(column_name)
			sum=0
			for row in from_final_data:
				sum+=int(row[column_index])
			xx.append(sum)
		else :
			print("Invalid Query with aggregate functions")
	print()
	for x in xx:
		print(x,end=" ")
	print()
#		except:
#			print("Invalid Query with aggregate functions")

elif(flag_groupby!=1 and str(list1[1])!="DISTINCT" and not(select_data[0]=="*" or select_data[0].startswith("count") or select_data[0].startswith("max") or select_data[0].startswith("min") or select_data[0].startswith("sum") or select_data[0].startswith("avg"))):
	try:
		col_index=[]
		for i in range(length):
			select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
			col_index.append(final_col_names.index(select_data[i]))
		for row in from_final_data:
			for i in col_index:
				print(row[i],end=" ") 
			print()
	except:
		print("invalid query")

elif(flag_groupby!=1 and str(list1[1])=="DISTINCT" and not(select_data[0]=="*" or select_data[0].startswith("count") or select_data[0].startswith("max") or select_data[0].startswith("min") or select_data[0].startswith("sum") or select_data[0].startswith("avg"))): 
	try:
		col_index=[]
		for i in range(length):
			select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
			col_index.append(final_col_names.index(select_data[i]))
		newList = [[each_list[i] for i in col_index] for each_list in from_final_data]
		#print(newList)
		from_final_data=[]
		for i in newList:
			if(i not in from_final_data):
				from_final_data.append(i)
		for qq in select_data:
			print(qq,end=" ")
		print()
		for x in from_final_data:
			for y in x:
				print(y,end=" ")
			print()
	except:
		print("Invalid Query")


elif(flag_groupby==1 and str(list1[1])!="DISTINCT"):

	for i in range(length):
		select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
	for i in select_data:
		print(i,end=" ")
	print()
	if group_data in select_data:
		if(len(select_data)==1):
			print(select_data[0])
			for i in d.keys():
				print(i)
		else:
			for row in d.keys():
				for i in select_data:
					if(i==group_data):
						print(row,end=" ")

					elif(i.startswith("sum")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						sum=0
						for l in d[row]:
							sum+=int(l[column_index])
						print(sum,end=" ")

					elif(i.startswith("avg")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						sum=0
						count=0
						for l in d[row]:
							sum+=int(l[column_index])
							count+=1
						if(count!=0):
							print(float(sum)/float(count),end=" ")	

					elif(i.startswith("min")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						min=0
						for l in d[row]:
							if(min>int(l[column_index])):
								min=int(l[column_index])
						print(min,end=" ")	

					elif(i.startswith("max")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						max=0
						for l in d[row]:
							if(max<int(l[column_index])):
								max=int(l[column_index])
						print(max,end=" ")	

					elif(i.startswith("count")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						count=0
						if(column_name=="*"):
							for l in d[row]:
								count+=1
						else:
							column_index=final_col_names.index(column_name)
							for l in d[row]:
								count+=1
						print(count,end=" ")	
					else:
						print("invalid query")
				print()	
	else:
		for row in d.keys():
				for i in select_data:

					if(i.startswith("sum")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						sum=0
						for l in d[row]:
							sum+=int(l[column_index])
						print()
						print(sum,end=" ")

					elif(i.startswith("avg")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						sum=0
						count=0
						for l in d[row]:
							sum+=int(l[column_index])
							count+=1
						if(count!=0):
							print(float(sum)/float(count),end=" ")	

					elif(i.startswith("min")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						min=0
						for l in d[row]:
							if(min>int(l[column_index])):
								min=int(l[column_index])
						print(min,end=" ")	

					elif(i.startswith("max")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						max=0
						for l in d[row]:
							if(max<int(l[column_index])):
								max=int(l[column_index])
						print(max,end=" ")	

					elif(i.startswith("count")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						count=0
						if(column_name=="*"):
							for l in d[row]:
								count+=1
						else:
							column_index=final_col_names.index(column_name)
							for l in d[row]:
								count+=1
						print(count,end=" ")	
					else:
						print("Invalid query")


elif(flag_groupby==1 and str(list1[1])=="DISTINCT"):
	for i in range(length):
		select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
	if group_data in select_data:
		if(len(select_data)==1):
			print(select_data[0])
			qqq=[]
			for i in d.keys():
				if i not in qqq:
					print(i)
					qqq.append(i)
		else:
			for row in select_data:
				print(row, end=" ")
			QQ1=[]
			for row in d.keys():
				sublist=[]
				for i in select_data:
					if(i==group_data):
						sublist.append(row)

					elif(i.startswith("sum")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						sum=0
						for l in d[row]:
							sum+=int(l[column_index])
						sublist.append(sum)

					elif(i.startswith("avg")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						sum=0
						count=0
						for l in d[row]:
							sum+=int(l[column_index])
							count+=1
						if(count==0):
							sublist.append("undefined")
						else:
							sublist.append(float(sum)/float(count))	

					elif(i.startswith("min")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						min=0
						for l in d[row]:
							if(min>int(l[column_index])):
								min=int(l[column_index])
						sublist.append(min)	

					elif(i.startswith("max")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						max=0
						for l in d[row]:
							if(max<int(l[column_index])):
								max=int(l[column_index])
						sublist.append(max)	

					elif(i.startswith("count")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						count=0
						if(column_name=="*"):
							for l in d[row]:
								count+=1
						else:
							column_index=final_col_names.index(column_name)
							for l in d[row]:
								count+=1
						sublist.append(count)	
					else:
						print("invalid query")

				if "undefined" not in sublist:
					if sublist not in QQ1:
						QQ1.append(sublist)	
	
			for row in QQ1:
				for i in row:
					print(i,end=" ")
				print()
	else:
		QQ1=[]
		for row in d.keys():
				sublist=[]
				for i in select_data:
					if(i.startswith("sum")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						sum=0
						for l in d[row]:
							sum+=int(l[column_index])
						sublist.append(sum)

					elif(i.startswith("avg")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						sum=0
						count=0
						for l in d[row]:
							sum+=int(l[column_index])
							count+=1
						if(count==0):
							sublist.append("undefined")
						else:
							sublist.append(float(sum)/float(count))	

					elif(i.startswith("min")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						min=0
						for l in d[row]:
							if(min>int(l[column_index])):
								min=int(l[column_index])
						sublist.append(min)	

					elif(i.startswith("max")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						max=0
						for l in d[row]:
							if(max<int(l[column_index])):
								max=int(l[column_index])
						sublist.append(max)	

					elif(i.startswith("count")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						count=0
						if(column_name=="*"):
							for l in d[row]:
								count+=1
						else:
							column_index=final_col_names.index(column_name)
							for l in d[row]:
								count+=1
						sublist.append(count)	
					else:
						print("Invalid query")
				if "undefined" not in sublist:
					if sublist not in QQ1:
						QQ1.append(sublist)
		for row in QQ1:
			for i in row:
				print(i,end=" ")
			print()
#except:
#	print("Invalid Query")

print()
print("******END OF QUERY OUTPUT********")