"""Build static HTML site from directory of HTML templates and plain files."""
import click
import pathlib
import jinja2
import json
import shutil

@click.command()
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output directory.")
def main(input_dir, output):
    """Generate static HTML files from templates and a config file """
    input_dir = pathlib.Path(input_dir)

    #find output directory  
    if output:
      output_dir = pathlib.Path(output)
    else:
      output_dir = input_dir / "html" #load whatevr html file we find
    print(f"DEBUG input_dir={input_dir}, output_dir={output_dir}")


    #copy static assets
    static_source_dir = input_dir / "static" #go to static folder
    if static_source_dir.is_dir(): #check if input folder actually has a static folder
      print(f"DEBUG: Found static directory at {static_source_dir}, copying assets...")
      shutil.copytree(
        static_source_dir, #project file
        output_dir, #path to destination file
        dirs_exist_ok=True
      )      

    template_dir = input_dir / "templates" #join directory paths so its somthing like filewefound/templates
    template_env = jinja2.Environment(
      loader=jinja2.FileSystemLoader(str(template_dir)),
      autoescape=jinja2.select_autoescape(['html', 'xml']),
    )
    print("Jinja2 enviroment initialized successfully!")


    #read json file
    config_path = input_dir / "config.json" #find json file
    with open(config_path, "r", encoding="utf-8") as config_file:
       config_list  = json.load(config_file)

    #grab the data from that json file
    for page in config_list:
      url = page["url"]
      template = page["template"]
      context = page["context"]

      template_obj = template_env.get_template(template)
      rendered_html = template_obj.render(context) 
      relative_url_path = url.strip("/") #take away the slash to recieve it as relative 
      output_file_path = output_dir / relative_url_path / "index.html" #output files must match the structure of the url, if url is / the file should be saved as index.html
      #if its smth like /users/awdeorio/ it sould created nested directories and name the file index.html

      #create a new file that doesnt exist yet, incase say we access a user and they dont exist... wellllll then
      #in that case we make a new file for that user           i.e. /users/cherrybomb/

      #we already have the file path in hand, now we need to use it to actually create le file
      output_file_path.parent.mkdir(parents=True, exist_ok=True) #this is how to make a file in python
      with open(output_file_path, "w", encoding="utf-8") as out_f:
        out_f.write(rendered_html) #now inside of that file we write our final html contents


    
    print("Static site generated successfully!")


if __name__ == "__main__":
  main()

  """
  python -m insta485generator insta485 -o insta485_html
  """