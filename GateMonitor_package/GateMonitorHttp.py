
from data.repo.Conections_repo import Conections_repo
from data.repo.Parans_repo import ParansRepo


class GateMonitorHttp():
    def __init__(self,host=0,port=0,db="GateMonitor_db"):
        self.host = host
        self.port = port
        self.repo_parans = ParansRepo(db)
        self.Conection_repo = Conections_repo(db)

    def HttpRequestGet(self,url,headers=None,params=None,method="GET"):
        import requests
        if method == "GET":
            Options_ =url.split("//")
            options = Options_[1].split("/")
            self.Conection_repo.CreateNewCon("0000",options[0],options[1])
            return requests.get(url,headers=headers)

        return requests.get(url,headers=headers)
        
    def CreateConfigsToServer(self,config,server):
        with open(f"config\\"+server+".gmc", "w") as f:
            f.write(config)

    def GetToken(self,ProjectName):
        return self.repo_parans.get_by_name("apptoken_"+ProjectName)