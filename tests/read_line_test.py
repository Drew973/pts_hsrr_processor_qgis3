#read line of readings .xls file
#read line of readings .xls file
def read_line(line,f_line,run):
    row=line.strip().split('\t')
    if is_valid(row):
        return {'raw_ch':float(row[0])*1000,'ts':row[1],'rl':row[2],'start_lon':row[12],'start_lat':row[13],'end_lon':row[14],'end_lat':row[15],'f_line':f_line,'run':run}
    


def is_valid(row):
    if len(row)>=15 and row[0]!='Position km':
        return row[0] and row[2]  and row[12] and row[13] and row[14] and row[15]
    

line='0.1000	15/05/2020 20:27:51	0	0	0	0	0		-26	5	42.88		-2.88727500	54.89589500	-2.88582167	54.89575500	-	-	-	=HYPERLINK("A69 DBFO EB CL1/0.011_3033867.jpg","0.011_3033867.jpg")	=HYPERLINK("A69 DBFO EB CL1/0.021_3034768.jpg","0.021_3034768.jpg")	=HYPERLINK("A69 DBFO EB CL1/0.032_3035671.jpg","0.032_3035671.jpg")	=HYPERLINK("A69 DBFO EB CL1/0.043_3036574.jpg","0.043_3036574.jpg")	=HYPERLINK("A69 DBFO EB CL1/0.053_3037475.jpg","0.053_3037475.jpg")	=HYPERLINK("A69 DBFO EB CL1/0.064_3038376.jpg","0.064_3038376.jpg")	=HYPERLINK("A69 DBFO EB CL1/0.074_3039276.jpg","0.074_3039276.jpg")	=HYPERLINK("A69 DBFO EB CL1/0.085_3040177.jpg","0.085_3040177.jpg")	=HYPERLINK("A69 DBFO EB CL1/0.096_3041077.jpg","0.096_3041077.jpg")'




print(read_line(line,2,'test_run'))
