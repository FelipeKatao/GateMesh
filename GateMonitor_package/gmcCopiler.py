

import requests


class GmcCopiler():
    def __init__(self,data):
        self.vars = {}
        self.parans = data
        self.errorRequest = []
        self.LimitRequest_ = 0
        self.LimitRequest_redirect = ""
        self.ServiceUse_ = ""
        self.absolute_request = ""

    def Compile(self,code):
        
        
        for i in code.split("\n"):
            if "var " in i:
                self.CreateVars(i)
            if "check_service" in i:
                self.check_service(str(i).replace("check_service","").replace(" ","").replace(':',"").replace("'","").strip())
            if "limit_request" in i and "if" not in i:
                self.LimitRequest(i)
            if "limit_request" in i and "if"  in i:
                self.ifLimitRequest(i)
            if "service_use" in i:
                self.ServiceUse(i)
            if "absolute_request" in i:
                self.absolute_request = str(i).replace("absolute_request","").replace(" ","").replace('',"").replace("'","").replace('"',"").strip()
            

    def CreateVars(self,comma):
        Code = str(comma).replace("var","").strip().split("=")
        self.vars[Code[0].strip()] = Code[1].replace('"',"").replace("'","").strip()
        return self.vars

    def check_service(self,ServiceName):
        url = self.parans["target"]+'/'+ServiceName
        result = requests.get(url)
        if result.status_code != 200:
            self.errorRequest.append(ServiceName)
            return False
        print(result)

    def LimitRequest(self,LimitRequest):
        LimitRequest = str(LimitRequest).split("=")[1].split()[0].replace('"',"").replace("'","").strip()
        if LimitRequest.isdigit():
            self.LimitRequest_ = int(LimitRequest)
        else:
            self.LimitRequest_ = int(self.vars[LimitRequest])
            
        print(self.LimitRequest_)
        return self.LimitRequest_

    def ifLimitRequest(self,LimitedRequest):
        LimitedRequest = str(LimitedRequest).split(":")[1].replace("redirect_to","").strip().replace('"',"").replace("'","").strip()
        self.LimitRequest_redirect = LimitedRequest
        return self.LimitRequest_redirect

    def ServiceUse(self,services):
        if '"' not in services:
            services = str(services).replace('"',"").replace("'","").strip()
            self.ServiceUse_ = self.vars[str(services).split("=")[1].split()[0].replace('"',"").replace("'","").strip()]
            return 0
        Services = str(services).split("=")[1].split()[0].replace('"',"").replace("'","").strip()
        self.ServiceUse_ = Services