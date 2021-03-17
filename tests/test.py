
def main():
    def std_replace(val):
        def test(inst):
            return "self.{}({})".format(val, ",".join(getattr(inst, "params", [])) + ",".join(inst.qubits))      
        return test

    def std_decomp(val):
        def test(lasdf):
            return ["not({},{})"]
        return test


    def std_test(val):
        def second_layer(dict_arg):
            return "first_arg ={}\nsecond_arg={}".format(val, dict_arg)        
        return second_layer

    decoding_dict = {
        "test": std_test(["1st_arg"]), 
        "x": std_replace("x"), 
        "h": std_replace("h"), 
        "rx": std_replace("rx"), 
    }

    print(decoding_dict["test"]("test"))
    print(decoding_dict[inst.name](inst))


if __name__ == "__main__":
    main()


def other():
    def std_replace(val):
        def test(inst):
            return "self.{}({})".format(val, ",".join(getattr(inst, "params", [])) + ",".join(inst.qubits))      
        return test
        def std_test(val):
        def second_layer(dict_arg):
            return "first_arg ={}\nsecond_arg={}".format(val, dict_arg)        
        return second_layer

    decoding_dict = {
        "test": std_test(["1st_arg"]), 
        "x": std_replace("x"), 
        "h": std_replace("h"), 
        "rx": std_replace("rx"), 
    }

    print(decoding_dict["test"]("test"))
    print(decoding_dict[inst.name](inst))