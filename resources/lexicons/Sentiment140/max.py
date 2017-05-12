


import sys



def main():


    filename = sys.argv[1]


    with open(filename,'r') as f:

        lines = f.readlines()


        current_max = abs(  float(lines[0].split()[2])  )

        for line in lines[1:]:

            candidate = float( line.split()[2] )

            if abs(candidate) > current_max:
                current_max = abs(candidate)


    print current_max



if __name__ == '__main__':
    main()
