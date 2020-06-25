import interfile
from ..scanner.compression import Compression

class header_location:
	def __init__(self, name, next_name=None, subname=None, list_value=None, list_index=None):
		self.name = name
		self.next_location = next_location # another header name
		self.subname = subname
		self.list_value = list_value
		self.list_index = list_index
	def __repr__(self):
		return "header_name({})".format(self.__dict__)

def extract_family(hdr, name):
	"""
		header is assumed to be the output of interfile.load(header_path), that is a parsed header file
		name is the start of a "matrix key", 
			e.g. "scale factor" corresponding to "scale factor ... [x]" 
			or "matrix size" corresponding to "matrix size [x]"
			where x is an integer
	"""
	matched_keys = []
	for key in hdr.keys():
		if key.count(name) > 0:
			matched_keys.append(key)
	def order(key):
		return key[-2] # extract x from "name ... [x]"
	matched_keys.sort(key=order)
	return [hdr[key]['value'] for key in matched_keys]

def find_header_value(header, header_location, default_value=None):
	"""
		header is assumed to be the output of interfile.load(header_path), that is a parsed header file
		in some cases, interfile assumes default values
	"""
	value = header.get(header_location.name)
	if value is None:
		if header_location.subname is not None: # handle e.g. matrix axis label[1]:= num_views ; matrix size[1]:= 400
			keys = header.keys()
			found_key = False
			for key in keys():
				found_key = key.count(self.subname) > 0
				if found_key: break
			if found_key:
				

				complement = key.replace(self.subname, "")
				found_match = False
				for match_key in keys():
					if match_key == key: continue
					found_math = match_key.count(complement) > 0
					if found_match: break
				if found_match:
					value = header.get(match_key)
		if header_location.next_location is not None:
			return find_header_value(header, header_location.next_location, default_value)
	if value is not None:
		value = value['value']
		if self.list_index is not None:
			return value[self.list_index]
		if self.list_value is not None:
			return value.count(self.list_value)
	else:
		return self.default_value

def compression_from_hdr(scanner, hdr_path, compression_obj = None, verbose = False):
	"""
		input: 
		scanner: an odlpet scanner object
		hdr_path: the path to a interfile header
		compression =None: a odlpet compression to update
		verbose = False: if verbose: print step commit descriptions
	"""
	if verbose: print("parse header file at path")
	hdr = interfile.load(path)
	if verbose: print("determine if listmode or sinogram")
	key = "SMS-MI header name space"
	value = hdr[key]['value']
	is_sinogram = value = "sinogram subheader"
	if verbose: print("assume data is {}, based on {}:=".format("sinogram" if is_sinogram else "listmode", name, value))
	is_sinogram2 = hdr_path.endswith(".s.hdr") # sanity check
	if is_sinogram != is_sinogram2:
		print("error, unexpected header content and file extension (e.g. '.s.hdr') mismatch")
	if compression_obj is None: 
		print("create scanner default compression")
		compression_obj = Compression(scanner)
	if verbose: print("create list of target odlpet compression attributes to update")
	attribute_names = ["span_num", "max_num_segments", "num_of_views", "num_non_arccor_bins", "data_arc_corrected"]
	hdr_names = ["axial compression", "maximum ring difference", "number of views", "number of projections", "applied corrections"]
	hdr_matrix_names = ["sinogram views", "sinogram projections"]
	n_easy = 2 
	n_matrix = 2
	if not is_sinogram: 
		n_easy = n_easy + n_matrix
		n_matrix = 0
	easy_attributes = attribute_names[:n_easy]
	matrix_attributes = attribute_names[n_easy:(n_easy+n_matrix)]
	attributes = [getattr(compression_obj, aname) for aname in attribute_names]
	if verbose: 
		pairs = [pair for pair in zip(attribute_names, attributes)]
		print("show target initial attributes (name, value) = {}".format(pairs))
	if verbose: print("search for corresponding compression parameters in hdr and update")

	def update_attr(name, value)
		if value is None:
			print("Error, no info on {} in header. Parameter not updated. ".format(name))
		else:
			setattr(compression_obj, name, value)		

	for name, hdr_name in zip(easy_attributes, hdr_names[:n_easy]):
		if verbose: print("attribute name = {}, interpret as {}".format(name, hdr_name))
		field = hdr.get(name)
		value = None if field is None else field['value']
		update_attr(name, value)

	if is_sinogram:
		if verbose: print("extract lists for matrix")
		hdr_families = ["matrix axis label", "matrix size"]
		matrix_info = [extract_family(hdr, family) for family in hdr_families]
		if verbose: 
			for pair in zip(hdr_families, matrix_info):
				print(pair)
		for name, hdr_name in zip(matrix_attributes, hdr_matrix_names):
			if verbose: 
				hdr_name2 = hdr_families[1] + " ({}) [{}]".format(index hdr_name, dim_index)
				print("attribute name = {}, interpret as {}".format(name, hdr_name2))
			if matrix_info[0].count(hdr_name) > 0:
				dim_index = matrix_info[0].find(hdr_name)
				value = matrix_info[1][dim_index]
			else:
				value = None
			update_attr(name, value)
	attr_index = -1
	name, hdr_name = attribute_names[attr_index], hdr_names[attr_index]
	hdr_value = "radial arc-correction"
	hdr_line = hdr.get(hdr_name)
	if verbose: 
		hdr_name2 = "'is {} one of the {}'".format(hdr_value, hdr_name)
		print("attribute name = {}, interpret as {}".format(name, hdr_name2))
	value = False # Siemens apparent default: unless stated, not corrected for
	if hdr_line is None:
		if verbose: print("no corrections")
	else:
		corrections = hdr_line['value'] # a sequence of applied corrections
		if verbose: print("{}:= {}".format(hdr_name, corrections))
		value = corrections.count(hdr_value) > 0
	update_attr(name, value)	
	if verbose: 
		pairs = [pair for pair in zip(attribute_names, attributes)]
		print("show target updated attributes (name, value) = {}".format(pairs))
	return compression