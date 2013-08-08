function count = countLines(fname)
% http://stackoverflow.com/questions/12176519/is-there-a-way-in-matlab-to-determine-the-number-of-lines-in-a-file-without-loop
fh = fopen(fname, 'rt');
% assert(fh == -1, 'Could not read: %s', fname);
x = onCleanup(@() fclose(fh));
count = 0;
while ~feof(fh)
    count = count + sum( fread( fh, 16384, 'char' ) == char(10) );
end
end