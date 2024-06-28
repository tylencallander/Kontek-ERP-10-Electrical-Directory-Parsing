import json
import os
import re

#   So far includes...

# - hmi_project, hmiprojectfiles, hmi_archive, hmiarchivefiles
# - plc_project, plcprojectfiles, plc_archive, plcarchivefiles
# - filename, filefullpath, filepath
# - isobsolete, rev, date
# - installations, installationinformationfullpath, installationinformationpath

#  To do...

# - combinedbom (Optional I think)
# - numberdrawingsets, drawingsets, pdfsfoldername, drawingname, numberrevisions
# - pdfdirectoryfullpath, pdfdirectorypath, pdffilefullpath, pdffilepath


def load_project_data(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def parse_file_details(file_path):
    filename = os.path.basename(file_path)
    details = {
        'filename': filename,
        'filefullpath': file_path,
        'filepath': file_path.split(os.sep),
        'isobsolete': 'OBSOLETE' in filename.upper()
    }
    rev_match = re.search(r'rev[ _]*(\d+)', filename, re.IGNORECASE)
    if rev_match:
        details['rev'] = rev_match.group(1)
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
    if date_match:
        details['date'] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    return details

def add_to_project_data(project_data, category, file_details, root):
    key_map = {
        'hmi_project': 'hmiprojectfiles',
        'hmi_archive': 'hmiarchivefiles',
        'plc_project': 'plcprojectfiles',
        'plc_archive': 'plcarchivefiles'
    }
    if 'INSTALLATION' in root.upper():
        category = 'installations'
        project_data[category] = {
            'installationinformationfullpath': file_details['filefullpath'],
            'installationinformationpath': file_details['filepath'],
            'filename': file_details['filename']
        }
    else:
        if category in key_map:
            specific_details = {
                f"{category[:-1]}fullpath": file_details['filefullpath'],
                f"{category[:-1]}path": file_details['filepath'],
                "filename": file_details['filename'],
                "isobsolete": file_details['isobsolete'],
                "date": file_details.get('date', ''),
                "rev": file_details.get('rev', '')
            }
            project_data.setdefault(key_map[category], []).append(specific_details)
        else:
            project_data.setdefault(category, []).append(file_details)

def check_directory_contents(project_details, expected_items):
    results = {}
    errors = {}

    for project, details in project_details.items():
        project_path = details.get('projectfullpath', '')
        electrical_path = os.path.join(project_path, 'ELECTRICAL')
        if not os.path.exists(electrical_path):
            errors[project] = "No ELECTRICAL directory"
            continue

        project_data = {}
        found_categories = set()

        for root, dirs, files in os.walk(electrical_path):
            for file in files:
                file_details = parse_file_details(os.path.join(root, file))
                for item, extensions in expected_items.items():
                    if file.endswith(tuple(extensions)):
                        add_to_project_data(project_data, item, file_details, root)
                        found_categories.add(item)

        missing_categories = set(expected_items.keys()) - found_categories
        if missing_categories:
            errors[project] = f"Missing categories: {', '.join(missing_categories)}"

        results[project] = {k: v for k, v in project_data.items() if v}

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

    print("Starting the checking of directory contents...")
    project_contents, project_errors = check_directory_contents(projects_details, expected_items)
    print("All projects processed.")

    with open('dir_details_elec.json', 'w') as f:
        json.dump(project_contents, f, indent=4)
        print("Directory details saved to dir_details_elec.json.")
    
    with open('errors.json', 'w') as f:
        json.dump(project_errors, f, indent=4)
        print("Errors saved to errors.json.")

    print("Processing complete. Check dir_details_elec.json and errors.json for output.")

if __name__ == "__main__":
    main()
