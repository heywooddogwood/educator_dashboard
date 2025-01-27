import solara

from ..database.class_report import Roster

@solara.component
def SetClass(class_id, roster, first_run = False, class_id_list = None):
    
    print('in SetClass')
    
    
    def on_value(value):
        print("SetClass: on_value", value)
        if value is None:
            print("SetClass: class_id is None")
            class_id.set(None)
            roster.set(None)
        elif first_run.value or (class_id.value != value):
            print("SetClass: class id", value)
            class_id.set(int(value))
            roster.set(Roster(int(value)))

    
    if first_run.value and class_id.value is not None:
        print("SetClass: first run", )
        on_value(class_id.value)
        first_run.set(False)
        

            
    
    
    if class_id.value is None:
        warning_text = """There was a problem with this class. Look at the python output to see what. We currently can't handle class ids below 183.
        This will be fixed in the future as we turn away from the old class_report code.            
            """
        solara.Markdown(warning_text, color='warning', style="font-size: 2em" )
    
    if class_id_list is None:
        solara.InputText(label="Class ID",  value = str(class_id), on_value=on_value)
    else:
        solara.Select(label="Class ID", values = class_id_list, value = class_id.value, on_value=on_value)
