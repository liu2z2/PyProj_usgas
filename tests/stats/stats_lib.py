# Author      : Zuguang Liu
# Date        : 2018-11-15 16:38:39
# Python Ver  : 3.6
# Description : 

import warnings
import pandas
import datetime
import numpy
import os
import operator

class gasStats():
	OPDICT={'<':operator.lt,'<=':operator.le,'==':operator.eq,'!=':operator.ne,'>':operator.gt,'>=':operator.ge}
	def __init__(self,st='',fileName=None):
		self.state=st
		if fileName==None:
			self.db=None
		else:
			self.db=self.csv2df(fileName)

	def importCSV(self,fileName):
		self.db=self.csv2df(fileName)

	def getPriceTable(self):
		return self.db[['price','date','service','city']].sort_values(by=['price']).reset_index(drop=True)

	def getOtherStats(self,subject):
		if self.db is None:
			raise Exception('No data has been imported')
		else:
			self.noWarn()
			pt=pandas.pivot_table(self.db,index=[subject],aggfunc=[len,numpy.mean,numpy.std,min,self.my25,self.my50,self.my75,max])
			pt=pt.loc[:, [('len', 'address'), ('mean', 'price'), ('min','price'),('my25', 'price'), ('my50', 'price'),('my75','price'),('max','price')]]
			pt.columns=['count','mean','min','25%','50%','75%','max']
			pt.index.name=subject
			return pt.sort_values(by=['mean']).reset_index()

	def filter(self,comps,gate='or'):
		self.noWarn()
		if not isinstance(comps,list):
			comps=[comps]
		for i in range(len(comps)):
			cond=comps[i]
			if i==0:
				boolIndex=self.OPDICT[cond[1]](self.db[cond[0]],cond[2])
			else:
				if gate=='and' or gate=='&':
					boolIndex=boolIndex&self.OPDICT[cond[1]](self.db[cond[0]],cond[2])
				if gate=='or' or gate=='|':
					boolIndex=boolIndex|self.OPDICT[cond[1]](self.db[cond[0]],cond[2])
		self.db=self.db[boolIndex]

	def getPriceStats(self):
		if len(self.db)==0:
			return {'state':self.state,'count':0}
		else:
			priceLst=list(self.db.price)
			return {'state':self.state,'count':len(priceLst),'mean':numpy.mean(priceLst),'min':min(priceLst),'25%':self.my25(priceLst),'50%':self.my50(priceLst),'75%':self.my75(priceLst),'max':max(priceLst)}

	def csv2df(self,fileName):
		df=pandas.read_csv(fileName)
		df['date']=[datetime.datetime.strptime(x, '%Y-%m-%d') for x in df['date']]
		df['city']=[x.split(',')[1].strip() for x in df['address']]
		return df

	def noWarn(self):
		warnings.simplefilter(action='ignore',category=FutureWarning)

	def my25(self,g):
		return numpy.percentile(g,25)

	def my50(self,g):
		return numpy.percentile(g,50)

	def my75(self,g):
		return numpy.percentile(g,75)

def USGasStats(dataDir,constrains=None):
	csvFiles = [f for f in os.listdir(dataDir) if f.endswith('.csv')]
	s=gasStats()
	tempLst=[]
	for f in csvFiles:
		s.state=f[4:6]
		s.importCSV(dataDir+f)
		if constrains!=None:
			s.filter(constrains)
		tempLst.append(s.getPriceStats())
	return pandas.DataFrame(tempLst,columns=tempLst[0].keys()).sort_values(by=['mean'])

def USGasToday():
	return USGasStats('../../database/',constrains=('date','==',datetime.datetime.today().date()))

def USGasThisWeek():
	return USGasStats('../../database/',constrains=('date','>',datetime.datetime.today().date()-datetime.timedelta(7)))

print(USGasToday())
print()
print(USGasThisWeek())

stat=gasStats(st='OH',fileName='../../database/gas_OH.csv')
print(stat.getOtherStats('service'))
print()
print(stat.getOtherStats('date'))
print()
print(stat.getOtherStats('city'))