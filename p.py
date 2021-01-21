import os
import re
import csv
import sqlparse
import itertools

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
	print("No semicolon at the end")
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
list=tuple(list) ##fixed
print(list)

index_of_from = list.index('FROM')
i=capital(list,index_of_from)

if(index_of_from+1<i):
	from_data=list[index_of_from+1:i]
else:
	from_data=list[i]

print(table_structure)
final_col_names=[]
if(type(from_data) == str):
	final_col_names.extend(table_structure[from_data.replace(',',"")])

from_final_data=[]

if(len(from_data)>1):
	final_col_names += table_structure[from_data[1].split(",")]
	for element in itertools.product(table_data[from_data[0].replace(',',"")],table_data[from_data[1].replace(',',"")]):
		from_final_data += element

else :
	from_final_data = table_data[from_data[0].replace(',',"")]
#print("final col names:")
#print(final_col_names)

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
	#print(order_data)
	try:
		index_of_orderby_in_columns=final_col_names.index(order_data)
		if(i+1==len(list) or list[i+1]=='ASC' or (list[i+1]!="ASC" and list[i+1]!="DESC")):
			from_final_data.sort(key = lambda x: x[index_of_orderby_in_columns])
		elif(list[i+1]=='DESC'):
			from_final_data.sort(key = lambda x: x[index_of_orderby_in_columns],reverse=True)

		#print("AFTER ORDER BY:")
		#print(from_final_data)
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
			print("query has some prob -  no such group by column name")
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
for i in select_data:
	print(i,end=" ")
print()
length=len(select_data)
i=0

if(flag_groupby!=1 and str(list1[1])!="DISTINCT" and (select_data[0]=="*" or select_data[0].startswith("count") or select_data[0].startswith("max") or select_data[0].startswith("min") or select_data[0].startswith("sum") or select_data[0].startswith("avg"))):
	for i in range(length):
		
		select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
		
		if(select_data[i]=="*" and flag_groupby!=1):
			print(from_final_data)
	
		elif(select_data[i].startswith("max") and flag_groupby!=1):
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
			print(float(sum)/float(count))
		
		elif(select_data[0].startswith("sum") and flag_groupby!=1):
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
			print("Inavlid Query")

elif(flag_groupby!=1 and str(list1[1])=="DISTINCT" and (select_data[0]=="*" or select_data[0].startswith("count") or select_data[0].startswith("max") or select_data[0].startswith("min") or select_data[0].startswith("sum") or select_data[0].startswith("avg"))):
	for i in range(length):		
		select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
		x=[]
		if(select_data[i]=="*" and flag_groupby!=1):
			for l in from_final_data:
				if l not in x:
					print(l)
	
		elif(select_data[i].startswith("max") and flag_groupby!=1):
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
				
				l1 = [] 
				count = 0
				for row in from_final_data:
					if(row not in l1):
						count+=1
				print(select_data[i])
				print(count)
			else:
				column_index=final_col_names.index(column_name)
				count=0
				l1 = [] 
				for row in from_final_data:
					if(row[column_index] not in l1):				
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
			x=[]
			for row in from_final_data:
				if(int(row[column_index]) not in x):
					sum+=int(row[column_index])
					count+=1
			print(select_data[i])
			print(float(sum)/float(count))
		
		elif(select_data[0].startswith("sum") and flag_groupby!=1):
			i1=str(select_data[i]).index("(")
			i2=str(select_data[i]).index(")")
			column_name=str(select_data[i])[i1+1:i2]
			column_index=final_col_names.index(column_name)
			sum=0
			x=[]
			for row in from_final_data:
				if(row[column_index] not in x):
					sum+=int(row[column_index])
			print(select_data[i])
			print(sum)

		else :
			print("Inavlid Query")
elif(flag_groupby!=1 and str(list1[1])!="DISTINCT" and not(select_data[0]=="*" or select_data[0].startswith("count") or select_data[0].startswith("max") or select_data[0].startswith("min") or select_data[0].startswith("sum") or select_data[0].startswith("avg"))):
	col_index=[]
	for i in range(length):
		select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
		col_index.append(final_col_names.index(select_data[i]))
	for row in from_final_data:
		for i in col_index:
			print(row[i],end=" ") 
		print()	


elif(flag_groupby!=1 and str(list1[1])=="DISTINCT" and not(select_data[0]=="*" or select_data[0].startswith("count") or select_data[0].startswith("max") or select_data[0].startswith("min") or select_data[0].startswith("sum") or select_data[0].startswith("avg"))): 
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
	print(from_final_data)


elif(flag_groupby==1 and str(list1[1])!="DISTINCT"):
	for i in range(length):
		select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
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
						print(sum," ")

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
						print(float(sum)/float(count)," ")	

					elif(i.startswith("min")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						min=0
						for l in d[row]:
							if(min>int(l[column_index])):
								min=int(l[column_index])
						print(min," ")	

					elif(i.startswith("max")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						max=0
						for l in d[row]:
							if(max<int(l[column_index])):
								max=int(l[column_index])
						print(max," ")	

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
								count+=l[count]
						print(count," ")	
					else:
						print("invalid query")
elif(flag_groupby==1 and str(list1[1])=="DISTINCT"):
	for i in range(length):
		select_data[i]=select_data[i].rstrip(" ").lstrip(" ")
	if group_data in select_data:
		if(len(select_data)==1):
			print(select_data[0])
			for i in d.keys():
				print(i)
		else:
			for i in select_data:
				print(i,end=" ")
			print()

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
						x=[]
						for l in d[row]:
							if l[column_index] not in x:
								sum+=int(l[column_index])
						print(sum," ")

					elif(i.startswith("avg")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						sum=0
						count=0
						x=[]	
						for l in d[row]:
							if l[column_index] not in x:
								sum+=int(l[column_index])
								count+=1
						print(float(sum)/float(count)," ")	

					elif(i.startswith("min")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						min=0
						for l in d[row]:
							if(min>int(l[column_index])):
								min=int(l[column_index])
						print(min," ")	

					elif(i.startswith("max")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						column_index=final_col_names.index(column_name)
						max=0
						for l in d[row]:
							if(max<int(l[column_index])):
								max=int(l[column_index])
						print(max," ")	

					elif(i.startswith("count")):
						i1=str(i).index("(")
						i2=str(i).index(")")
						column_name=str(i)[i1+1:i2]
						count=0
						if(column_name=="*"):
							x=[]
							for l in d[row]:
								if l not in x:
									count+=1
						else:
							column_index=final_col_names.index(column_name)
							x=[]
							for l in d[row]:
								if l[column_index] not in x:
									count+=1
						print(count," ")	
					else :
						print("Inavlid Query")
	else:
		print("Invalid select column")
print()
print("**************")