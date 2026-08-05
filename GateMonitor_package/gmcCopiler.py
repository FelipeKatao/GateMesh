

import requests


class GmcCopiler():
    def __init__(self,data):
        self.vars = {}
        self.parans = data
        self.errorRequest = []
        self.LimitRequest_ = 0
        self.LimitRequest_redirect = ""
        self.RedirectFail  =""
        self.ServiceUse_ = ""
        self.absolute_request = ""
        self.check = True
        self.colector_ = False
        self.resource_allow =True

    def Compile(self,code):
        headers = code.split("\n")
        headers_values = {}
        for i in headers:
            if "@use selector_service" in i:
                for i in code.split("\n"):
                    if "@"+ self.parans["service"] in i:
                        headers_values[self.parans["service"].replace('"',"").replace("'","").strip()] = []
                        self.colector_ = True
                    if "@end" in i:
                        self.colector_ = False
                    if  self.colector_:
                         headers_values[self.parans["service"]].append(i)
        

        if headers_values != {}:
            code = headers_values[self.parans["service"]]
        else:
            code = code.split("\n")

        for i in code:
            if "allow_resource_for" in i:
                self.allow_resource_for(i)
            if "var " in i:
                self.CreateVars(i)
            if "check_service" in i:
              self.check=  self.check_service(str(i).replace("check_service","").replace(" ","").replace(':',"").replace("'","").strip())
            if "limit_request" in i and "if" not in i:
                self.LimitRequest(i)
            if "limit_request" in i and "if"  in i:
                self.ifLimitRequest(i)
            if "check_fail" in i and "if"  in i:
                self.ifLimitRequestFail(i)
            if "service_use" in i:
                self.ServiceUse(i)
            if "absolute_request" in i:
                self.absolute_request = str(i).replace("absolute_request","").replace(" ","").replace('',"").replace("'","").replace('"',"").strip()
            

    def CreateVars(self,comma):
        Code = str(comma).replace("var","").strip().split("=")
        self.vars[Code[0].strip()] = Code[1].replace('"',"").replace("'","").strip()
        return self.vars

    def check_service(self,ServiceName):
        if '"' not in  ServiceName :
            ServiceName = self.vars[ServiceName]
            
        if "{@parans}" in ServiceName:
            ServiceName = self.parans["service"]
        url = self.parans["target"]+'/'+ServiceName
        result = requests.get(url)
        if result.status_code != 200:
            self.errorRequest.append(ServiceName)
            return False
        return True
    def LimitRequest(self,LimitRequest):
        
        LimitRequest = str(LimitRequest).split("=")[1].split()[0].replace('"',"").replace("'","").strip()
        if LimitRequest.isdigit():
            self.LimitRequest_ = int(LimitRequest)
        else:
            self.LimitRequest_ = int(self.vars[LimitRequest])
        return self.LimitRequest_

    def ifLimitRequest(self,LimitedRequest):
        LimitedRequest = str(LimitedRequest).split(":")[1].replace("redirect_to","").strip().replace('"',"").replace("'","").strip()
        self.LimitRequest_redirect = LimitedRequest
        return self.LimitRequest_redirect

    def ifLimitRequestFail(self,LimitedRequest):
            LimitedRequest = str(LimitedRequest).split(":")[1].replace("redirect_to","").strip().replace('"',"").replace("'","").strip()
            self.RedirectFail = LimitedRequest
            return self.RedirectFail

    def ServiceUse(self,services):
        if '"' not in services:
            services = str(services).replace('"',"").replace("'","").strip()
            self.ServiceUse_ = self.vars[str(services).split("=")[1].split()[0].replace('"',"").replace("'","").strip()]
            return 0
        Services = str(services).split("=")[1].split()[0].replace('"',"").replace("'","").strip()
        self.ServiceUse_ = Services

    def allow_resource_for(self,resource):
        Res = str(resource).split(":")[1].split()[0].replace('"',"").replace("'","").strip()
        Res= Res.replace("'","").split(",")
        if self.parans["userToken"] not in Res:
            self.resource_allow = False
            return {"error":"Resource not Autorized"}

    