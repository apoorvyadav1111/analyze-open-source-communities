class ToxicityConfig:
  token = ""
  def __init__(self, token=None,file=None):
    if token:
      self.token = token

    elif file:
      with open(file,'r') as f:
        data = f.read()

      if data:
        self.token = data