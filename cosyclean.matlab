% Temperature data is read,  the data is then
% cleaned of outliers, if present. The cleaned data is written to another
% channel for storage.

% Channel ID to read data from
readChannelID = 75136;
% Temperature Field ID
TemperatureFieldID = 1;

% To store the cleaned temperature data, write it to a channel other than
% the one used for reading data. To write to a channel, assign the write
% channel ID to the 'writeChannelID' variable, and the write API Key to the
% 'writeAPIKey' variable below. Find the write API Key in the right side pane
% of this page.

writeChannelID = 205353;
writeAPIKey = 'AOG2IC2RJK8KI7T7';

% Read the last 200 temperature data points from the CosyHutch channel
[tempC, timeStamp] = thingSpeakRead(readChannelID, 'fields', TemperatureFieldID, 'numPoints', 200);

% Use a simple threshold based outlier elimination
% technique. We fetched the last 200 points added to the read channel above and now
% check if there any values greater than 40 C. If any such points are found, delete
% them.

% Check for outliers

anyOutliers = sum(tempC > 40);

% If any outliers are found in the data
if anyOutliers > 0

    % Find the indices of elements which are not outliers
    cleanDataIndex = find(tempC <= 40);

    % Select only elements that are not outliers
    cleanData = tempC(cleanDataIndex);

    % Select only timestamps corresponding to clean data
    cleanTimeStamps = timeStamp(cleanDataIndex);

else
    % If no outliers are found, then the data is directly used
    cleanData = tempC;
    cleanTimeStamps = timeStamp;
end

display(cleanData, 'Cleaned data');

% Write the cleaned temperature to other channel 
thingSpeakWrite(writeChannelID, cleanData, 'Timestamp', cleanTimeStamps, 'Writekey', writeAPIKey);

