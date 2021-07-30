import os 


#reads text file, splits into sql files or sql commands seperated by ; then runs them in order.
 #try/except in file with gui
def runSetupFile(con,file,folder):
  
    with open(os.path.join(folder,file)) as f:
        
        for c in f.read().split(';'):
            com = c.strip()
            f = os.path.join(folder,com)
            if com:
                if os.path.exists(f):
                    runScript(con,f)
                else:
                    con.cursor().execute(com) 
 
    
 
def runScript(con,script,args={}):
        s = script
        
        if os.path.dirname(script)=='':
            s = os.path.join(os.path.dirname(__file__),script)
    
        with open(s,'r') as f:
            if args:
                con.cursor().execute(f.read(),args)
            else:
                con.cursor().execute(f.read())
                
                
                
                