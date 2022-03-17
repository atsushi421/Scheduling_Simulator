import json
from sys import argv

class SchedulingViewer:
	OFFSET_X = 0
	OFFSET_Y = 150
	HEIGHT = 150
	WIDTH  = 40
	FONT_SIZE = HEIGHT/3
	X_UNIT = 150
	HEIGHT_UNIT = 500

	color_list = ["AliceBlue","AntiqueWhite","Aqua","Aquamarine","Azure","Beige","Bisque","Black","BlanchedAlmond","Blue","BlueViolet","Brown","BurlyWood","CadetBlue","Chartreuse","Chocolate","Coral","CornflowerBlue","Cornsilk","Crimson","Cyan","DarkBlue","DarkCyan","DarkGoldenRod","DarkGray","DarkGreen","DarkGrey","DarkKhaki","DarkMagenta","DarkOliveGreen","Darkorange","DarkOrchid","DarkRed","DarkSalmon","DarkSeaGreen","DarkSlateBlue","DarkSlateGray","DarkSlateGrey","DarkTurquoise","DarkViolet","DeepPink","DeepSkyBlue","DimGray","DimGrey","DodgerBlue","FireBrick","FloralWhite","ForestGreen","Fuchsia","Gainsboro","GhostWhite","Gold","GoldenRod","Gray","Green","GreenYellow","Grey","HoneyDew","HotPink","IndianRed","Indigo","Ivory","Khaki","Lavender","LavenderBlush","LawnGreen","LemonChiffon","LightBlue","LightCoral","LightCyan","LightGoldenRodYello","LightGray","LightGreen","LightGrey","LightPink","LightSalmon","LightSeaGreen","LightSkyBlue","LightSlateGray","LightSlateGrey","LightSteelBlue","LightYellow","Lime","LimeGreen","Linen","Magenta","Maroon","MediumAquaMarine","MediumBlue","MediumOrchid","MediumPurple","MediumSeaGreen","MediumSlateBlue","MediumSpringGreen","MediumTurquoise","MediumVioletRed","MidnightBlue","MintCream","MistyRose","Moccasin","NavajoWhite","Navy","OldLace","Olive","OliveDrab","Orange","OrangeRed","Orchid","PaleGoldenRod","PaleGreen","PaleTurquoise","PaleVioletRed","PapayaWhip","PeachPuff","Peru","Pink","Plum","PowderBlue","Purple","Red","RosyBrown","RoyalBlue","SaddleBrown","Salmon","SandyBrown","SeaGreen","SeaShell","Sienna","Silver","SkyBlue","SlateBlue","SlateGray","SlateGrey","Snow","SpringGreen","SteelBlue","Tan","Teal","Thistle","Tomato","Turquoise","Violet","Wheat","White","WhiteSmoke","Yellow","YellowGreen"]

	def __init__(self, input_filename, output_filename, ex_rate):
		self.input_filename = input_filename
		self.output_filename = output_filename
		self.color_count = 0
		self.color_hash = {}

		if ex_rate == 0:
			json_file = open(self.input_filename)
			json_data = json.load(json_file)
			ex_rate = 96 / json_data["makespan"]
			print("ex_rate    : auto_fix")

		SchedulingViewer.WIDTH *= ex_rate
		print("ex_rate    : "+str(ex_rate))

	def print_svg(self):
		json_file = open(self.input_filename)
		json_data = json.load(json_file)
		self.core_num = json_data["coreNum"]
		self.makespan = json_data["makespan"]

		self.write_header(self.core_num * SchedulingViewer.HEIGHT, self.makespan * SchedulingViewer.WIDTH + SchedulingViewer.OFFSET_X)
		self.draw_lines(self.core_num * SchedulingViewer.HEIGHT, self.makespan)
		
		for task in json_data["taskSet"]:
			self.draw_task(task["coreID"], task["taskName"], task["startTime"], task["executionTime"])
		  #for test
		  #100.times{|i|
		#	draw_task(rand(10),"task_#{i}", rand(100), rand(500)+10)
		#  }
		self.write_script()
		self.write_footer()


	def draw_lines(self, height, width):
		output_file = open(self.output_filename, "a")
		n = int(width / SchedulingViewer.X_UNIT) + 2
		for i in range(n):
			x = i * SchedulingViewer.X_UNIT * SchedulingViewer.WIDTH + SchedulingViewer.OFFSET_X
			text_x = i * SchedulingViewer.X_UNIT

			output_file.write("\t\t<line id =\"line_"+str(text_x)+"\" class=\"selectable\" x1=\""+str(x)+"\" y1=\"0\" x2=\""+str(x)+"\" y2=\""+str(height)+"\" stroke-width=\"15\" stroke=\"black\" />\n")
			output_file.write("\t\t<text id =\"line_"+str(text_x)+"-info\" x=\""+str(x)+"\" y=\"100\"  font-family=\"Verdana\" font-size=\""+str(SchedulingViewer.FONT_SIZE * 2)+"\" stroke=\"blue\">")
			output_file.write(str(i * SchedulingViewer.X_UNIT)+"</text>\n")
		"""
  			(height/HEIGHT_UNIT).times{|y|
  				#print "\t\t<text id =\"line_#{text_x}-info\" x=\"#{x}\" y=\"#{y*HEIGHT_UNIT}\"  font-family=\"Verdana\" font-size=\"#{FONT_SIZE*2}\" stroke=\"blue\" opacity=\"0.0\">"
  				print "\t\t<text id =\"line_#{text_x}-info\" x=\"#{x}\" y=\"#{y*HEIGHT_UNIT}\"  font-family=\"Verdana\" font-size=\"#{FONT_SIZE*2}\" stroke=\"blue\">"
  				puts  "#{i * X_UNIT / 10}</text>"
  			}
		"""

	def draw_task(self, core_id, task_name, start_time, exection_time):
		output_file = open(self.output_filename, "a")

		if task_name not in self.color_hash:
			self.color_hash[task_name] = SchedulingViewer.color_list[self.color_count] 
			self.color_count = (self.color_count + 1) % len(SchedulingViewer.color_list)

		color = self.color_hash[task_name]
		x = start_time * SchedulingViewer.WIDTH + SchedulingViewer.OFFSET_X
		y = core_id * SchedulingViewer.HEIGHT + SchedulingViewer.OFFSET_Y
		w = exection_time * SchedulingViewer.WIDTH

		#puts  "\t\t<rect id =\"#{task_name}\" class=\"selectable\" x=\"#{start_time*WIDTH + OFFSET_X}\" y=\"#{core_id*HEIGHT + OFFSET_Y}\" width=\"#{exection_time*WIDTH}\" height=\"#{HEIGHT-10}\" stroke=\"black\" fill=\"white\" stroke-width=\"2\" />"
		output_file.write("\t\t<rect id =\""+str(task_name)+"_"+str(start_time)+"\" class=\"selectable\" x=\""+str(x)+"\" y=\""+str(y)+"\" width=\""+str(w)+"\" height=\""+str(SchedulingViewer.HEIGHT - 10)+"\" stroke=\"black\" fill=\""+str(color)+"\" stroke-width=\"2\" />\n")
		output_file.write("\t\t<text id =\""+str(task_name)+"_"+str(start_time)+"\" class=\"selectable\" x=\""+str(x)+"\" y=\""+str(y + SchedulingViewer.FONT_SIZE)+"\"             width=\""+str(w + SchedulingViewer.OFFSET_X)+"\" font-family=\"Verdana\" font-size=\""+str(SchedulingViewer.FONT_SIZE)+"\"> "+str(task_name)+" </text>\n")
		output_file.write("\t\t<text id =\""+str(task_name)+"_"+str(start_time)+"-info\" x=\""+str(x)+"\" y=\""+str(y + SchedulingViewer.FONT_SIZE + SchedulingViewer.HEIGHT / 2)+"\" width=\""+str(w + SchedulingViewer.OFFSET_X)+"\" font-family=\"Verdana\" font-size=\""+str(SchedulingViewer.FONT_SIZE)+"\" stroke=\"blue\" opacity=\"0.0\">")
		#puts  "#{task_name}@#{core_id}:#{start_time}~#{start_time+exection_time}</text>"
		output_file.write(str(start_time)+"~"+str(start_time+exection_time)+"@"+str(core_id)+"</text>\n")
		output_file.close()

	def print_style(self):
		output_file = open(self.output_filename, "a")
		output_file.write("\t\t<style>\n")
		output_file.write("\t\t.selectable:hover {\n")
		output_file.write("\t\t\tfill: orange;\n")
		output_file.write("\t\t\tstroke: orange;\n")
		output_file.write("\t\t}\n")
		output_file.write("\t\t.shown {\n")
		output_file.write("\t\t\topacity: 1;\n")
		output_file.write("\t\t}\n")
		output_file.write("\t\t</style>\n")
		output_file.close()

	def write_header(self, height, width):
		output_file = open(self.output_filename, "w")
		output_file.write("<html>\n")
		output_file.write("\t<body>\n")
		output_file.close()

		self.print_style()
		
		output_file = open(self.output_filename, "a")
		output_file.write("\t<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n")
		#puts "\t<svg width=\"#{width}\" height=\"#{height}\"  xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">"
		output_file.write("\t<svg width=\""+str(width)+"\" height=\""+str(height)+"\" viewBox=\"0 0 "+str(height)+" "+str(width)+"\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n")
		output_file.close()

	def write_script(self):
		output_file = open(self.output_filename, "a")
		output_file.write("\t\t<script>\n")
		output_file.write("\t\tlet selectableElements = document.getElementsByClassName(\"selectable\");\n")
		output_file.write("\t\tArray.from( selectableElements ).forEach(elem => {\n")
		output_file.write("\t\t\telem.addEventListener(\"mouseover\", eve => {\n")
		output_file.write("\t\t\t\tlet textId = elem.id + \"-info\";\n")
		output_file.write("\t\t\t\tlet textElem = document.getElementById(textId);\n")
		output_file.write("\t\t\t\tif( textElem != null ) {\n")
		output_file.write("\t\t\t\t\ttextElem.classList.add(\"shown\");\n")
		output_file.write("\t\t\t\t}\n")
		output_file.write("\t\t\t});\n")
		output_file.write("\t\t\telem.addEventListener(\"mouseleave\", eve => {\n")
		output_file.write("\t\t\t\tlet textId = elem.id + \"-info\";\n")
		output_file.write("\t\t\t\tlet textElem = document.getElementById(textId);\n")
		output_file.write("\t\t\t\tif( textElem != null ) {\n")
		output_file.write("\t\t\t\t\ttextElem.classList.remove(\"shown\");\n")
		output_file.write("\t\t\t\t}\n")
		output_file.write("\t\t\t});\n")
		output_file.write("\t\t});\n")
		output_file.write("\t\t</script>\n")
		output_file.close()

	def write_footer(self):
		output_file = open(self.output_filename, "a")
		output_file.write("\t\t</svg>\n")
		output_file.write("\t</body>\n")
		output_file.write("</html>\n")
		output_file.close()

"""
opt = OptionParser.new
opt.on('-o') {|v| puts "test #{v}" }
opt.on('--[no-]bar') {|v| p v }
opt.parse!(ARGV)
p ARGV
"""

input_file = argv[1] if len(argv) > 1 else "sample.json"
output_file = argv[2] if len(argv) > 2 else "output.html"
ex_rate = float(argv[3]) if len(argv) > 3 else 0

print("input_file : "+input_file)
print("output_file: "+output_file)
svg_viewer = SchedulingViewer(input_file, output_file, ex_rate)
svg_viewer.print_svg()


"""
print_header(10000, $core_num * HEIGHT)
draw_task(1, "task1", 0, 10)
draw_task(2, "task2", 0, 20)
100.times{|i|
	draw_task(rand(10),"task_#{i}", rand(100), rand(500)+10)
}
print_script()
print_footer()
"""
