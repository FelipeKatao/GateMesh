
import requests

from GateMonitor_package.gmcCopiler import GmcCopiler
from data.repo.Conections_repo import Conections_repo
from data.repo.Parans_repo import ParansRepo

    

class GateMonitorHttp():
    def __init__(self,data,host=0,port=0,db="GateMonitor_db"):
        self.host = host
        self.port = port
        self.repo_parans = ParansRepo(db)
        self.Conection_repo = Conections_repo(db)
        self.Gmc_code = GmcCopiler(data)
        self.parans = data
        self.Value_response = ""

    def HttpRequestGet(self,url,headers=None,params=None,method="GET"):
        import requests
        if method == "GET":
            Options_ =url.split("//")
            options = Options_[1].split("/")
            self.Conection_repo.CreateNewCon("0000",options[0],options[1])
            return requests.get(url,headers=headers)

        return requests.get(url,headers=headers)
        
    def CreateConfigsToServer(self,config,server):
        with open(f"config\\"+server+".gmc", "w" ,encoding= "utf-8") as f:
            f.write(config)

    def GetToken(self,ProjectName):
        return self.repo_parans.get_by_name("apptoken_"+ProjectName)

    def ExecuteGmcFile(self,code):
        self.Gmc_code.Compile(code)

        #Verificar permissão
        if self.Gmc_code.resource_allow == False:
            return {"error":"Resource not Autorized"}
        #validar serviço disponivel
        if self.Gmc_code.check == False:
             if self.Gmc_code.RedirectFail != "":
                 if self.Gmc_code.absolute_request:
                      return self.HttpRequestGet(self.Gmc_code.absolute_request+"/"+self.Gmc_code.RedirectFail,headers=self.parans)
                 return self.HttpRequestGet(self.parans["target"]+"/"+self.Gmc_code.RedirectFail,headers=self.parans)
             return self.HttpRequestGet(self.parans["target"]+"/"+self.Gmc_code.ServiceUse_,headers=self.parans)

        # Validar Load Balance 
        if self.Gmc_code.ServiceUse_ == "{@parans}":
             self.Gmc_code.ServiceUse_ = self.parans["service"]
        Count = self.Conection_repo.CountCons(self.Gmc_code.ServiceUse_,self.parans["target"].replace("http://","").replace("https://",""))
        if  int(Count) > int(self.Gmc_code.LimitRequest_):
            if self.Gmc_code.absolute_request:
                if self.Gmc_code.LimitRequest_redirect == "":
                    return {"error":"LimitRequest"}
                return self.HttpRequestGet(self.Gmc_code.absolute_request+"/"+self.Gmc_code.LimitRequest_redirect,headers=self.parans)
            return self.HttpRequestGet(self.parans["target"]+"/"+self.Gmc_code.LimitRequest_redirect,headers=self.parans)
        else:
           return self.HttpRequestGet(self.parans["target"]+"/"+self.Gmc_code.ServiceUse_,headers=self.parans)