
class ModelError(Exception):

    def __init__(self, message, model=None, params=None):

        self.message = message
        self.model = model
        self.params = params

    def __str__(self):

        if self.model and self.params:
            message = "Model error: {}\nmodel:{}\nparams:{}".format(self.message, str(self.model), str(self.params))
        elif self.model:
            message = "Model error: {}\nmodel:{}".format(self.message, str(self.model))
        elif self.params:
            message = "Model error: {}\nparams:{}".format(self.message, str(self.params))
        else:
            message = "Model error: {}".format(self.message)

        return message


class SubprocessError(Exception):

    def __init__(self, message, command=None):

        self.message = message
        self.model = command 

    def __str__(self):

        message = '' 
        if self.command:
            message = "{}\ncommand:{}".format(self.message, self.command)
        else:
            message = self.message

        return message

if __name__ == '__main__':

    raise ModelError("TEST")

