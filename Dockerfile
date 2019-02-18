FROM centos:7
WORKDIR /
RUN yum group install "Development Tools" -y
RUN yum install git wget tar zlib-devel -y
WORKDIR /usr/local/src
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /usr/local/conda
ENV PATH="/usr/local/conda/bin:$PATH"
RUN source /usr/local/conda/bin/activate
RUN conda update -n base -c defaults conda
RUN ln -s /usr/local/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh
RUN conda create -n python36 python==3.6.7
RUN echo "source activate python36" > ~/.bashrc
ENV PATH /usr/local/conda/envs/python36/bin:$PATH
RUN conda install -n python36 -y -c conda-forge pip
RUN mkdir -p /opt/software/
WORKDIR /opt/software/
RUN git clone https://github.com/EI-CoreBioinformatics/mikado.git
WORKDIR /opt/software/mikado
RUN sed -i 's/;.*//' requirements.txt
RUN conda install -n python36 --update-all -y -c conda-forge -c bioconda -c anaconda --file requirements.txt
RUN python setup.py bdist_wheel
RUN pip install dist/*whl
CMD mikado