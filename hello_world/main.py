class Greeter:
    def __init__(self):
        pass

    def greet(self):
        return 'Hello World!'


def main():
    print('Running main function')
    Greeter().greet()
    print('Finished main function')


if __name__ == "__main__":
    main()
