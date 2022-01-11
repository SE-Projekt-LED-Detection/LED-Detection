# clean
rm -r leddet
mkdir leddet

# pull new repo
cd leddet && git clone https://github.com/morgenmuesli/LED-Detection.git

# checkout last branch
cd LED-Detection && git checkout $1
