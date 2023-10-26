import os
import argparse
import openai
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

system_prompt = """
You are a P4 code assistant that helps to insert "// MARKER" into P4 code.
You will get P4 code as input, together with the instructions.
Finally, return modified P4 code as output.
"""
# Look for action blocks that looks like this: action YYYY(...)\{\}, where YYY are the action names, and insert the code "MARKER" in it.
# Also, insert the "MARKER" into all if-else statements.
# For the output, return the code after adding the "MARKER"s.

# You are tasked to add markers in the form of  "dce##();" into the following P4 code, where ## can range from 00 to 99. 
# Add the markers into all if-else statements, switch cases, action blocks, and apply blocks within the "control ingress" block.
# Do not insert dce##(); in the actions list (actions = { ... }) of a table.
# Only give the modified code of the control ingress block as output.
# Only give the code as output.

p4_code = ""
with open('output/program_000.p4') as f:
    p4_code = f.read()

instruction = """
INSTRUCTIONS:
First, insert "// MARKER" into all if-else statements. 
Then, find all action blocks that are in the form of "action YYYY(ZZZ)\{\}" where YYY are the action names and ZZZ are action parameters, insert "// MARKER" too.
Make sure not to insert "// MARKER" in any table scope.
CODE:
"""

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
#   model="gpt-3.5-turbo-16k",
  messages=[
    {
      "role": "system",
      "content": system_prompt
    },
    {
      "role": "user",
      "content": instruction + p4_code
    }
  ],
  temperature=0,
  max_tokens=2048,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

print(response)
with open('marked/program_000.p4', 'w') as f:
    f.write(response.choices[0].message.content)

# def main():
#     parser = argparse.ArgumentParser()

#     parser.add_argument(
#         '--output-path', required=True, default='./output/',
#         help='output path for the generated p4 programs'
#     )

#     parser.add_argument(
#         '--max-tokens', type=int, default=1800,
#         help='maximum number of tokens in a p4 program'
#     )

#     parser.add_argument(
#         '--num-programs', type=int, default=100,
#         help='number of p4 programs to generate'
#     )

#     args = parser.parse_args()
#     pprint(args)
    
#     output_path = args.output_path
#     arch = args.arch
#     max_tokens = args.max_tokens
#     num_programs = args.num_programs 

#     if not os.path.exists(output_path):
#         os.mkdir(output_path)

#     assert os.path.exists(output_path)
        
# if __name__ == '__main__':
#     main()