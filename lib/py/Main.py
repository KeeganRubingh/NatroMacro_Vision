import easygui, Annotations

def trainMenu():
    def Annotate():
        Annotations.StartAnnotatingImages()
    def EditImages():
        Annotations.StartEditingImages()
        
    trainMenuDefs = {
        "Capture Annotations": Annotate,
        "Edit Annotations": EditImages
    }
    trainMenuDefs[easygui.choicebox("Datasets Menu","Datasets Menu",trainMenuDefs)]()
    

def homeMenu():
    homeMenuDefs = {
        "Training":trainMenu,
        "Exit":exit
    }
    homeMenuDefs[easygui.choicebox("Home Menu","Home Menu",homeMenuDefs)]()

if(__name__ == "__main__"):
    homeMenu()