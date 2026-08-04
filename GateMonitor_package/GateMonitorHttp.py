
from data.repo.Parans_repo import ParansRepo


class GateMonitorHttp():
    def __init__(self,host=0,port=0,db="GateMonitor_db"):
        self.host = host
        self.port = port
        self.repo_parans = ParansRepo(db)

    def HttpRequestGet(self,url,headers=None,params=None,method="GET"):
        import requests
        if method == "GET":
            return requests.get(url,headers=headers)

        return requests.get(url,headers=headers)
        
    def CreateConfigsToServer(self,config,server):
        with open(f"config\\"+server+".gmc", "w") as f:
            f.write(config)

    def GetToken(self,ProjectName):
        print("apptoken_"+ProjectName)
        return self.repo_parans.get_by_name("apptoken_"+ProjectName)