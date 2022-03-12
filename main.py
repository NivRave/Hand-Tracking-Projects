import HandTrackingModule as hmt

def main():
    model = hmt.HandDetector()
    model.run()

if __name__ == "__main__":
    main()