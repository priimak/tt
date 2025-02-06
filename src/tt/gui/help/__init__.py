HELP = {
    "view_subplot_edit":
        """
        <html>
        <H3>View Subplot Configuration</H3>
        <ul>
        <li><em><b>Left Y-Axis Label<b></em> - label to be shown on the left y-axis. Note that even<br/>if set 
        it will not appear if there are no traces that use left y-axis.<br/></li>
        <li><em><b>Right Y-Axis Label</b></em> - label to be shown on the right y-axis. Note that even<br/>if set 
        it will not appear if there are no traces that use left y-axis.<br/></li>
        <li><em><b>X-Axis Label</b></em> - label to be shown on the x-axis. Note that if set, then<br/>time unit 
        (as configured in the project) will also be appended to this label.<br/></li>
        <li><em><b>Show Grid</b></em> - is grid to be shown in this subplot.<br></li>
        <li><em><b>Legends Location</b></em> - where to place legends on this subplot if there are any.<br/>
        Set to [<em>None</em>] if you do not want to legends to be shown at all. Note that even<br/>
        if "Legends Location" is set to something which is not [<em>None</em>], legends will be<br/>shown only if
        there is at least one trace (configured below) that indicates that<br/>it is to be accompanied by
        a legend.</li>
        </ul> 
        <H3>Traces in Subplot</H3>
        <ul>
        <li><em><b>Trace</b></em> - trace label.<br/></li>
        <li><em><b>Version</b></em> - trace version to be shown. -1 always refers to the latest version.<br/></li>
        <li><em><b>Color</b></em> - color for this trace. Setting to [<em>auto</em>] will ensure no color collisions
        <br/> between multiple traces.<br/></li>
        <li><em><b>On Axis</b></em> - <em>left</em> or <em>right</em> axis. Use different axis when you have
        two traces<br/>with wildly different scales on y-axis.<br/></li>
        <li><em><b>Show Overlay</b></em> - show or no-show overlay signal if trace is configured to<br/>
        produce one. For example low pass filtered signal. Note that overlay needs<br/>
        to be defined in the config for this trace.<br/></li>
        <li><em><b>Show Legends</b></em> - show or no-show legends associated with this trace. Global<br/>
        <em>Legends Location</em> value (see above) could suppress overall display of legends for<br/>
        this subplot if it is set to [<em>None</em>]. Note that if trace is configured to compute basic<br/>
        statistics (for example mean or standard deviation), that statistic will show in the<br/>
        legends for the trace. Hence, if you want to see those stat. values you will need to<br/>
        enable showing legends.<br/></li>
        </ul>
        </html>       
        """,
    "trace_config_dialog":
        """
        <html>
        <ul>
        <li><em><b>Figure title</b></em> - text that will appear right above the trace plot<br/></li>
        <li><em><b>Show Legend</b></em> - show or no-show legend associated with this trace. If enabled<br/>
        legend text is a trace label optionally followed values of stat. functions (see below).<br/>
        If multiple traces are rendered, then label will also include trace version number.<br/></li>
        <li><em><b>Legend Location</b></em> - position in the plot where legend will be placed.<br/></li>
        <li><em><b>X-Axis Label</b></em> - label to be shown on the x-axis. Note that if set, then<br/>
        time unit (as configured in the project) will also be appended to this label.<br/></li>
        <li><em><b>Y-Axis Label</b></em> - label to be shown on the y-axis.<br/></li>
        <li><em><b>Show Grid</b></em> - is grid to be shown in this plot.<br></li>
        <li><em><b>Linear Transform</b></em> - <code>Y' = scale * Y + offset</code><br/></li>
        <li><em><b>Overlay Filtered Signal</b></em> - add signal that passed through one of two filters.<br>
            <ul>
            <li><em><b>Savitsky-Golay</b></em> - savgol filter. Associated parameter is window<br/>
            width which could be in percentage of data points (add '%' sign) or in<br/>
            absolute number of data points.<br/></li>
            <li><em><b>Lowpass</b></em> - digital Butterworth lowpass filter. Associated parameter is<br/>
            cutoff frequency and must include unit such KHz, MHz and so on.<br/></li>
            </ul>
        </li>
        <li><em><b>Stat Functions</b></em> - functions to compute for this trace. Possible
        functions are<br/><em>min</em>, <em>max</em>, <em>range = max - min</em>, <em>mean</em>, <em>stdev</em>.
        If configured, computed values<br/>will appear in the legend. Thus to see them you need 
        make sure that<br/><em>Show Legend</em> (see above) is checked. </li>
        </ul>
        </html>
        """
}
