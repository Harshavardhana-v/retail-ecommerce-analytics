import java.io.IOException;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class Top20Mapper
        extends Mapper<Object, Text, Text, IntWritable> {

    private final Text productId = new Text();
    private final IntWritable quantity = new IntWritable();

    @Override
    public void map(Object key, Text value, Context context)
            throws IOException, InterruptedException {

        String line = value.toString().trim();

        if (line.isEmpty()) {
            return;
        }

        String[] fields = line.split("\\s+");

        if (fields.length != 2) {
            return;
        }

        try {
            productId.set(fields[0]);
            quantity.set(Integer.parseInt(fields[1]));

            context.write(productId, quantity);

        } catch (NumberFormatException e) {
            // Ignore invalid records
        }
    }
}