# Locations
BIN := ./bin
SRC := ./src
LIB := ./lib

# C++ compiler flags.
CXX   := g++ -g -Wall 
FLAGS := -std=c++17 $(shell root-config --cflags) $(shell correction config --cflags --ldflags) -I/cvmfs/cms.cern.ch/el9_amd64_gcc12/external/boost/1.80.0-4e27c6908892e3529bfbcf4445a96fe6/include

LIBS  := $(shell root-config --libs) $(shell correction config --cflags --ldflags) -L/cvmfs/cms.cern.ch/el9_amd64_gcc12/external/boost/1.80.0-4e27c6908892e3529bfbcf4445a96fe6/lib

# Analyzer sources and header
ANALYZER_SRC := $(SRC)/LeptonEfficiencyCorrector.cc \
				$(SRC)/JetCorrector.cc \
				$(SRC)/MainEvent.cc \
				$(SRC)/RoccoR.cc \
				$(SRC)/WeightCalculatorFromHistogram.cc \
				$(SRC)/HmmAnalyzer.cc

ANALYZER_HEADERS := $(LIB)/BTagCalibrationStandalone.h \
				$(LIB)/LeptonEfficiencyCorrector.h \
				$(LIB)/JetCorrector.h \
				$(LIB)/MainEvent.h \
				$(LIB)/RoccoR.h \
				$(LIB)/WeightCalculatorFromHistogram.h \
				$(LIB)/HmmAnalyzer.h


# Tuple sources and header
TUPLE_SRC := $(SRC)/CreateTuple.cc
TUPLE_HEADERS := $(LIB)/Run3Constants.h $(LIB)/Constants.h $(LIB)/CreateTuple.h

# Histogram sources and header
SKIM_ggH_SRC := $(SRC)/SkimTuplesggH.cc
SKIM_VBF_SRC := $(SRC)/SkimTuples_VBF.cc
SKIM_HEADERS := $(LIB)/Run3Constants.h $(LIB)/Constants.h

SOURCES := $(ANALYZER_SRC) $(HISTOGRAM_SRC) $(SKIM_ggH_SRC) $(SKIM_VBF_SRC) $(TUPLE_SRC)


# Object files
ANALYZER_OBJECTS := LeptonEfficiencyCorrector.o \
				JetCorrector.o \
				MainEvent.o \
				RoccoR.o \
				WeightCalculatorFromHistogram.o \
				HmmAnalyzer.o
 


TUPLE_OBJECTS := CreateTuple.o

SKIM_ggH_OBJECTS := SkimTuplesggH.o
SKIM_VBF_OBJECTS := SkimTuples_VBF.o

OBJECTS := $(ANALYZER_OBJECTS) $(TUPLE_OBJECTS)

# Executables
ANALYZER_EXECUTABLE := $(BIN)/HmmAnalyzer
SKIM_ggH_EXECUTABLE := $(BIN)/SkimTuplesggH
SKIM_VBF_EXECUTABLE := $(BIN)/SkimTuples_VBF
TUPLE_EXECUTABLE := $(BIN)/CreateTuple

# Default target: build both executables
.PHONY: all
all: $(ANALYZER_EXECUTABLE) $(SKIM_ggH_EXECUTABLE) $(SKIM_VBF_EXECUTABLE) $(TUPLE_EXECUTABLE)

# Compile only the Analyzer
.PHONY: analyzer
analyzer: $(ANALYZER_EXECUTABLE)

# Compile only the tuples 
.PHONY: tuple
tuple: $(TUPLE_EXECUTABLE)

# Compile only the Skim ggH
.PHONY: skim
skim: $(SKIM_ggH_EXECUTABLE)

# Compile only the Skim VBF
.PHONY: skim_vbf
skim: $(SKIM_VBF_EXECUTABLE)

# Compile all the objects
$(OBJECTS): %.o: $(SRC)/%.cc $(LIB)/%.h
#$(OBJECTS): %.o: $(SOURCES) $(LIB)/%.h
	@echo "Compiling $<..."
	$(CXX) $(FLAGS) -c $< -o $@

# Special rule for SkimTuplesggH.o without a header file
$(SKIM_ggH_OBJECTS): %.o: $(SRC)/%.cc
	@echo "Compiling $<..."
	$(CXX) $(FLAGS) -c $< -o $@

# Special rule for SkimTuples_VBF.o without a header file
$(SKIM_VBF_OBJECTS): %.o: $(SRC)/%.cc
	@echo "Compiling $<..."
	$(CXX) $(FLAGS) -c $< -o $@

# Linking for HmmAnalyzer
$(ANALYZER_EXECUTABLE): $(ANALYZER_OBJECTS)
	@echo "Linking $(ANALYZER_EXECUTABLE)..."
	$(CXX) $(FLAGS) -o $@ $^ $(LIBS)
	@echo "done"

# Linking for CrekteHistograms
$(HISTOGRAM_EXECUTABLE): $(HISTOGRAM_OBJECTS)
	@echo "Linking $(HISTOGRAM_EXECUTABLE)..."
	$(CXX) $(FLAGS) -o $@ $^ $(LIBS)
	@echo "done"

# Linking for Tuples
$(TUPLE_EXECUTABLE): $(TUPLE_OBJECTS)
	@echo "Linking $(TUPLE_EXECUTABLE)..."
	$(CXX) $(FLAGS) -o $@ $^ $(LIBS)
	@echo "done"

# Linking for Skim ggH tuples
$(SKIM_ggH_EXECUTABLE): $(SKIM_ggH_OBJECTS)
	@echo "Linking $(SKIM_ggH_EXECUTABLE)..."
	$(CXX) $(FLAGS) -o $@ $^ $(LIBS)
	@echo "done"

# Linking for Skim VBF tuples
$(SKIM_VBF_EXECUTABLE): $(SKIM_VBF_OBJECTS)
	@echo "Linking $(SKIM_VBF_EXECUTABLE)..."
	$(CXX) $(FLAGS) -o $@ $^ $(LIBS)
	@echo "done"
	
# Specifying the object files as intermediates deletes them automatically after the build process.
.INTERMEDIATE: $(ANALYZER_OBJECTS) $(HISTOGRAM_OBJECTS) $(SKIM_ggH_OBJECTS) $(SKIM_VBF_OBJECTS) $(TUPLE_OBJECTS)

# Clean target
.PHONY: clean
clean:
	rm -f $(ANALYZER_OBJECTS) $(HISTOGRAM_OBJECTS) $(SKIM_ggH_OBJECTS) $(SKIM_VBF_OBJECTS) $(TUPLE_OBJECTS)	$(ANALYZER_EXECUTABLE) $(HISTOGRAM_EXECUTABLE) $(SKIM_ggH_EXECUTABLE) $(SKIM_VBF_EXECUTABLE) $(TUPLE_EXECUTABLE)
