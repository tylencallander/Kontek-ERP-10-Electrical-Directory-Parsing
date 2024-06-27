import json
import os

def load_project_data(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def check_directory_contents(project_details, expected_items):
    results = {}
    errors = {}

    for project, details in project_details.items():
        project_path = details.get('projectfullpath', '')
        electrical_path = os.path.join(project_path, 'ELECTRICAL')

        if not os.path.exists(electrical_path):
            continue 

        found_files = {}
        project_errors = []

        for root, dirs, files in os.walk(electrical_path):
            for file in files:
                for item in expected_items:
                    if file.endswith(tuple(expected_items[item])):
                        if item not in found_files:
                            found_files[item] = []
                        found_files[item].append({
                            'filename': file,
                            'filefullpath': os.path.join(root, file),
                            'filepath': os.path.join(root, file).split(os.sep)
                        })

        for item, extensions in expected_items.items():
            if item not in found_files:
                project_errors.append(f"{item} missing")

        results[project] = found_files
        if project_errors:
            errors[project] = project_errors

    return results, errors

def main():
    projects_data_path = "P:/KONTEK/ENGINEERING/ELECTRICAL/Application Development/ERP/5. Kontek Project Directory Standard/V1_2024_06_20/projectfolders.json"
    projects_details = load_project_data(projects_data_path)

    expected_items = {
        'boms': ['xlsx', 'xls'],
        'schematics': ['pdf', 'dwg'],
        'hmi_project': ['mer', 'ap13', 'ap14', 'ap15', 'ap16', 'ap18', 'ccwsln'],
        'hmi_archive': ['apa', 'zap13', 'zap14', 'zap15', 'zap16', 'zap18'],
        'plc_project': ['ACD', 'ap13', 'ap14', 'ap15', 'ap16', 'ap18', 'ccwsln', 'RSS'],
        'plc_archive': ['zap13', 'zap14', 'zap15', 'zap16', 'zap18'],
        'plc_hmi_project': ['ap13', 'ap14', 'ap15', 'ap16', 'ap18', 'ccwsln'],
        'plc_hmi_archive': ['zap13', 'zap14', 'zap15', 'zap16', 'zap18']
    }

    project_contents, project_errors = check_directory_contents(projects_details, expected_items)

    with open('dir_details_elec.json', 'w') as f:
        json.dump(project_contents, f, indent=4)
    
    with open('errors.json', 'w') as f:
        json.dump(project_errors, f, indent=4)

    print("Processing complete. Check dir_details_elec.json and errors.json for output.")

if __name__ == "__main__":
    main()